from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from agents.recommender import generate_recommendation
from api.ai import run_ai
from api.deps import ai_budget, owned_session
from api.schemas import SourceOut
from services.analytics import (
    get_dsa_average,
    get_dsa_topic_scores,
    get_readiness_score,
    get_resume_fit_score,
    get_score_by_topic,
    get_theory_average,
    get_theory_trend,
    get_weakest_topics,
)
from services.dsa_service import list_attempts

router = APIRouter(prefix="/sessions/{session_id}/dashboard", tags=["dashboard"])


class TrendPoint(BaseModel):
    date: datetime | None = None
    topic: str | None = None
    score: int


class TopicScore(BaseModel):
    topic: str
    average_score: float
    count: int = 0  # how many scored answers or attempts the average is based on


class DashboardOut(BaseModel):
    readiness: int | None
    theory_average: float | None
    resume_fit: int | None
    dsa_average: float | None
    theory_count: int
    dsa_attempts: int
    trend: list[TrendPoint]
    dsa_trend: list[TrendPoint]
    by_topic: list[TopicScore]
    weakest: list[TopicScore]
    dsa_topics: list[TopicScore]


class RecommendIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    topic: str = Field(min_length=1, max_length=80)


class RecommendOut(BaseModel):
    advice: str
    sources: list[SourceOut]


def _with_counts(scores: list[dict], entries: list[dict]) -> list[dict]:
    """Add how many entries each topic average is based on (the analytics service returns only the average)."""
    counts: dict[str, int] = {}
    for entry in entries:
        if entry.get("topic"):
            counts[entry["topic"]] = counts.get(entry["topic"], 0) + 1
    return [{**s, "count": counts.get(s["topic"], 0)} for s in scores]


@router.get("", response_model=DashboardOut)
def dashboard(session: dict = Depends(owned_session)):
    # The same analytics calls ui/dashboard_page.py makes.
    sid = session["id"]
    trend = get_theory_trend(sid)
    attempts = list_attempts(sid)
    dsa_trend = sorted(
        ({"date": a["created_at"], "topic": a["topic"], "score": a["score"]} for a in attempts if a["score"] is not None),
        key=lambda p: p["date"] or datetime.min,
    )
    return DashboardOut(
        readiness=get_readiness_score(sid),
        theory_average=get_theory_average(sid),
        resume_fit=get_resume_fit_score(sid),
        dsa_average=get_dsa_average(sid),
        theory_count=len(trend),
        dsa_attempts=len(attempts),
        trend=trend,
        dsa_trend=dsa_trend,
        by_topic=_with_counts(get_score_by_topic(sid), trend),
        weakest=_with_counts(get_weakest_topics(sid, n=3), trend),
        dsa_topics=_with_counts(get_dsa_topic_scores(sid), dsa_trend),
    )


@router.post("/recommendation", response_model=RecommendOut)
def recommendation(body: RecommendIn, session: dict = Depends(owned_session), spend=Depends(ai_budget)):
    spend()
    return run_ai(generate_recommendation, session["id"], body.topic)
