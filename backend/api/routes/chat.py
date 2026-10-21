from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from api.ai import run_ai
from api.deps import ai_budget, owned_session
from api.schemas import SourceOut
from graphs.rag_graph import rag_graph
from services.session_service import list_documents

router = APIRouter(prefix="/sessions/{session_id}/chat", tags=["chat"])


class ChatIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    question: str = Field(min_length=2, max_length=1000)


class ChatOut(BaseModel):
    answer: str
    sources: list[SourceOut]
    retrieved_count: int
    kept_count: int
    retry_count: int
    sub_questions: list[str]


@router.post("", response_model=ChatOut)
def ask(body: ChatIn, session: dict = Depends(owned_session), spend=Depends(ai_budget)):
    if not list_documents(session["id"]):
        raise HTTPException(status.HTTP_409_CONFLICT, "Add a document to this session first.")

    spend()
    # Exactly what ui/chat.py does: invoke the compiled graph with the question and session id.
    result = run_ai(rag_graph.invoke, {"question": body.question, "session_id": session["id"]})

    return ChatOut(
        answer=result["answer"],
        sources=result.get("sources", []),
        retrieved_count=len(result.get("documents", [])),
        kept_count=len(result.get("relevant_documents", [])),
        retry_count=result.get("retry_count", 0),
        sub_questions=result.get("sub_questions", []),
    )
