import re
import shutil
from datetime import datetime
from pathlib import Path

import pymupdf
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from langchain_core.documents import Document as LCDocument
from pydantic import BaseModel, ConfigDict, Field

from api.config import Settings
from api.data import delete_chunks, delete_document_row, get_document, vector_write_lock
from api.deps import get_settings, owned_session
from rag.config import UPLOADS_DIR
from rag.indexer import index_documents, list_indexed_documents
from rag.splitter import split_documents
from rag.vector_store import create_vector_store
from services.session_service import list_documents, record_document

router = APIRouter(prefix="/sessions/{session_id}/documents", tags=["documents"])

DOC_TYPES = {"company", "jd", "resume", "notes", "experience"}
JD_TEXT_NAME = "job-description.txt"


class DocumentOut(BaseModel):
    id: int
    file_name: str
    doc_type: str | None
    chunk_count: int
    indexed_at: datetime | None = None
    # False when the database remembers the file but the vector store no longer has it
    # (for example after a host restart wiped local storage). None = could not check.
    indexed: bool | None = None


class TextIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    doc_type: str
    name: str = Field(default="", max_length=60)
    text: str = Field(min_length=20, max_length=50000)


def _check_type(doc_type: str) -> str:
    if doc_type not in DOC_TYPES:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Unknown document type.")
    return doc_type


def _safe_name(name: str, suffix: str) -> str:
    base = Path(name or "document").name
    stem = re.sub(r"[^A-Za-z0-9._ -]", "_", Path(base).stem).strip(" ._") or "document"
    return f"{stem[:60]}{suffix}"


def _present(session_id: str) -> set[str] | None:
    try:
        return set(list_indexed_documents(session_id))
    except Exception:
        return None


def _out(doc: dict, present: set[str] | None) -> DocumentOut:
    return DocumentOut(
        id=doc["id"],
        file_name=doc["file_name"],
        doc_type=doc["doc_type"],
        chunk_count=doc["chunk_count"] or 0,
        indexed_at=doc["indexed_at"],
        indexed=None if present is None else doc["file_name"] in present,
    )


def _room_left(session: dict, settings: Settings) -> None:
    if len(list_documents(session["id"])) >= settings.max_docs_per_session:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"A session holds at most {settings.max_docs_per_session} documents. Remove one first.",
        )


def _name_free(session: dict, file_name: str) -> None:
    if any(d["file_name"] == file_name for d in list_documents(session["id"])):
        raise HTTPException(status.HTTP_409_CONFLICT, f"'{file_name}' is already in this session. Remove it first.")


@router.get("", response_model=list[DocumentOut])
def list_session_documents(session: dict = Depends(owned_session)):
    present = _present(session["id"])
    return [_out(d, present) for d in list_documents(session["id"])]


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_pdf(
    session: dict = Depends(owned_session),
    settings: Settings = Depends(get_settings),
    file: UploadFile = File(...),
    doc_type: str = Form(...),
):
    _check_type(doc_type)
    file_name = _safe_name(file.filename or "", ".pdf")
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Only PDF files are accepted.")
    _room_left(session, settings)
    _name_free(session, file_name)

    data = file.file.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE, f"That file is over {settings.max_upload_bytes // (1024 * 1024)} MB."
        )
    if not data.startswith(b"%PDF-"):
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "That does not look like a PDF.")
    try:
        with pymupdf.open(stream=data, filetype="pdf") as pdf:
            if pdf.needs_pass:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Password-protected PDFs are not supported.")
            if pdf.page_count > settings.max_pdf_pages:
                raise HTTPException(
                    status.HTTP_413_CONTENT_TOO_LARGE, f"PDFs can have at most {settings.max_pdf_pages} pages."
                )
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "That PDF could not be read.") from error

    folder = UPLOADS_DIR / session["id"]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / file_name
    try:
        path.write_bytes(data)
        with vector_write_lock:
            chunk_count = index_documents([path], session["id"], doc_type=doc_type)
        record = record_document(
            session_id=session["id"],
            file_name=file_name,
            file_path=str(path),
            doc_type=doc_type,
            chunk_count=chunk_count,
        )
    except ValueError as error:  # e.g. a scanned PDF with no extractable text
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error)) from error
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Indexing failed. Try again in a moment.") from error
    finally:
        # The text now lives in the vector store; do not keep strangers' files on disk.
        shutil.rmtree(folder, ignore_errors=True)
    return _out(record, None)


@router.post("/text", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def add_text(
    body: TextIn,
    session: dict = Depends(owned_session),
    settings: Settings = Depends(get_settings),
):
    """Index pasted text (for example a job description) with the same splitter and vector
    store as an uploaded PDF, using the same metadata fields."""
    _check_type(body.doc_type)
    if len(body.text) > settings.max_text_chars:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, f"Pasted text is limited to {settings.max_text_chars} characters.")
    file_name = _safe_name(body.name, ".txt") if body.name else JD_TEXT_NAME
    _room_left(session, settings)
    _name_free(session, file_name)

    page = LCDocument(
        page_content=body.text,
        metadata={
            "source": f"{session['id']}/{file_name}",
            "file_name": file_name,
            "session_id": session["id"],
            "doc_type": body.doc_type,
            "page": 0,
        },
    )
    chunks = split_documents([page])
    try:
        with vector_write_lock:
            create_vector_store(chunks)
        record = record_document(
            session_id=session["id"],
            file_name=file_name,
            file_path="",
            doc_type=body.doc_type,
            chunk_count=len(chunks),
        )
    except Exception as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Indexing failed. Try again in a moment.") from error
    return _out(record, None)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(document_id: int, session: dict = Depends(owned_session)):
    doc = get_document(session["id"], document_id)
    if doc is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found.")
    delete_chunks(session["id"], doc["file_name"])
    delete_document_row(session["id"], document_id)
