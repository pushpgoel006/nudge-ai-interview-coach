"""Helpers the API needs that the existing services do not offer.

They only read and write through the existing models and the existing vector-store
loader. Nothing in the AI pipeline (loading, splitting, embedding, retrieval, graphs)
is changed or re-implemented here.
"""

import threading
from datetime import datetime, timedelta

from api import usage
from api.threads import store
from database.db import get_db
from database.models import Document, DsaAttempt, Followup, Interview, PrepSession, ResumeReview, User
from rag.retriever import load_vector_store

# Chroma's local persistent store is not built for concurrent writers, so every write
# the API makes to it is serialized behind this lock.
vector_write_lock = threading.Lock()


def get_document(session_id: str, document_id: int) -> dict | None:
    with get_db() as db:
        doc = db.query(Document).filter(Document.id == document_id, Document.session_id == session_id).first()
        if doc is None:
            return None
        return {"id": doc.id, "file_name": doc.file_name, "doc_type": doc.doc_type}


def delete_document_row(session_id: str, document_id: int) -> None:
    with get_db() as db:
        db.query(Document).filter(Document.id == document_id, Document.session_id == session_id).delete()


def delete_chunks(session_id: str, file_name: str | None = None) -> int:
    """Remove a session's chunks from the vector store (all of them, or one file's)."""
    where = {"session_id": session_id}
    if file_name is not None:
        where = {"$and": [{"session_id": session_id}, {"file_name": file_name}]}
    with vector_write_lock:
        vectors = load_vector_store()
        ids = vectors.get(where=where).get("ids", [])
        if ids:
            vectors.delete(ids=ids)
    return len(ids)


# ---------------------------------------------------------------------------
# Account removal
# ---------------------------------------------------------------------------


def delete_user_everything(user_id: str) -> int:
    """Remove a user and everything they own: vectors, documents, rounds, reviews, attempts,
    sessions, usage records and the account itself. Returns how many sessions were removed."""
    with get_db() as db:
        session_ids = [s.id for s in db.query(PrepSession).filter(PrepSession.owner_id == user_id).all()]

    for sid in session_ids:
        try:
            delete_chunks(sid)
        except Exception:  # a missing or unreachable vector store must not block deleting the account
            pass

    with get_db() as db:
        if session_ids:
            interview_ids = [i.id for i in db.query(Interview).filter(Interview.session_id.in_(session_ids)).all()]
            if interview_ids:
                db.query(Followup).filter(Followup.interview_id.in_(interview_ids)).delete(synchronize_session=False)
            db.query(Interview).filter(Interview.session_id.in_(session_ids)).delete(synchronize_session=False)
            db.query(ResumeReview).filter(ResumeReview.session_id.in_(session_ids)).delete(synchronize_session=False)
            db.query(DsaAttempt).filter(DsaAttempt.session_id.in_(session_ids)).delete(synchronize_session=False)
            db.query(Document).filter(Document.session_id.in_(session_ids)).delete(synchronize_session=False)
            db.query(PrepSession).filter(PrepSession.id.in_(session_ids)).delete(synchronize_session=False)
        db.query(User).filter(User.id == user_id).delete(synchronize_session=False)

    usage.delete_user_events(user_id)
    store.drop_user(user_id)
    return len(session_ids)


def list_expired_accounts(days: int, keep_emails: tuple[str, ...] = ()) -> list[dict]:
    """Accounts created more than `days` days ago (minus `keep_emails`). Read-only."""
    if days <= 0:
        return []
    cutoff = datetime.utcnow() - timedelta(days=days)
    with get_db() as db:
        return [
            {"id": u.id, "email": u.email, "created_at": u.created_at}
            for u in db.query(User).filter(User.created_at < cutoff).all()
            if u.email not in keep_emails
        ]


def purge_expired_accounts(days: int, keep_emails: tuple[str, ...] = ()) -> int:
    """PERMANENTLY delete the accounts `list_expired_accounts` returns. Returns the count."""
    old = list_expired_accounts(days, keep_emails)
    for account in old:
        delete_user_everything(account["id"])
    return len(old)
