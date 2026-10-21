from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.ai import run_ai
from api.deps import ai_budget, owned_session
from graphs.resume_graph import resume_graph
from services.resume_service import get_latest_review

router = APIRouter(prefix="/sessions/{session_id}/resume", tags=["resume"])


class VerdictOut(BaseModel):
    requirement: str
    verdict: str
    evidence: str | None = None


class ReviewOut(BaseModel):
    id: int | None = None
    overall_score: int
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    suggestions: str = ""
    created_at: datetime | None = None
    # Present only right after a run. A saved review keeps just matched and missing skills.
    verdicts: list[VerdictOut] | None = None


@router.get("", response_model=ReviewOut | None)
def latest(session: dict = Depends(owned_session)):
    return get_latest_review(session["id"])


@router.post("/check", response_model=ReviewOut)
def check(session: dict = Depends(owned_session), spend=Depends(ai_budget)):
    spend()
    # Exactly what ui/resume_page.py does: invoke the compiled graph with the session id.
    result = run_ai(resume_graph.invoke, {"session_id": session["id"]})
    review = result["review"]
    if "error" in review:
        # e.g. "Upload a resume to this session before running the check." (no LLM call was made)
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, review["error"])
    return review
