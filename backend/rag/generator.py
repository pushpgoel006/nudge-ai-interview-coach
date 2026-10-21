from pathlib import Path

from langchain_core.documents import Document

from models.llm_provider import get_llm
from prompts.rag_prompts import RAG_PROMPT

def _label(document: Document) -> str:
    metadata = document.metadata or {}
    name = metadata.get("file_name")
    if not name:
        source = metadata.get("source")
        name = Path(source).name if source else "document"
    page = int(metadata.get("page", 0)) + 1
    return f"[{name} | p.{page} | {metadata.get('doc_type') or 'document'}]"


# helps to merge the used chunks
def format_context(documents: list[Document]) -> str:
    # Label every excerpt with its file, page and type so the model can tell the documents apart,
    # cite them, and connect what one document says with what another says.
    return "\n\n".join(
        f"{_label(document)}\n{document.page_content}"
        for document in documents
    )

#helps generate answer
def generate_answer(
    question: str,
    documents: list[Document],
) -> str:
    

    context = format_context(documents)

    prompt = RAG_PROMPT.format(
        context=context,
        question=question,
    )

    llm = get_llm()

    response = llm.invoke(prompt)

    return response.content