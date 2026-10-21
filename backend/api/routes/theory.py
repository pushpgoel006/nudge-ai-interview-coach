from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from agents.question_generator import generate_grounded_question
from api.ai import run_ai
from api.deps import ai_budget, current_user, owned_session
from api.schemas import SourceOut
from api.threads import store
from graphs.interview_graph import interview_graph
from services.session_service import list_documents

router = APIRouter(prefix="/sessions/{session_id}/theory", tags=["theory"])

KIND = "theory"


class StartIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    topic: str | None = Field(default=None, max_length=80)
    difficulty: Literal["easy", "medium", "hard"] = "medium"


class AnswerIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    answer: str = Field(min_length=2, max_length=4000)


class QuestionOut(BaseModel):
    thread_id: str
    question: str
    sources: list[SourceOut]
    followup_number: int
    topic: str | None = None


class TurnOut(BaseModel):
    followup_number: int
    question: str
    answer: str
    score: int
    strengths: str
    weaknesses: str
    ideal_answer: str
    grounded: bool
    sources: list[SourceOut]


class NextOut(BaseModel):
    question: str
    sources: list[SourceOut]
    followup_number: int


class AnswerOut(BaseModel):
    turn: TurnOut
    next: NextOut | None
    done: bool


@router.post("/start", response_model=QuestionOut)
def start(body: StartIn, session: dict = Depends(owned_session), user: dict = Depends(current_user), spend=Depends(ai_budget)):
    if not list_documents(session["id"]):
        raise HTTPException(status.HTTP_409_CONFLICT, "Add a document to this session first.")

    spend()
    # Same call as the "New Question" button in ui/interview_page.py.
    result = run_ai(generate_grounded_question, session["id"], topic=body.topic or None, difficulty=body.difficulty)

    thread_id = store.create(
        user["id"],
        session["id"],
        KIND,
        {
            "question": result["question"],
            "sources": result.get("sources", []),
            "followup_number": 0,
            "done": False,
            # Starting state handed to interview_graph; replaced by each graph result.
            "state": {"session_id": session["id"], "topic": result.get("topic"), "difficulty": body.difficulty},
        },
    )
    return QuestionOut(
        thread_id=thread_id,
        question=result["question"],
        sources=result.get("sources", []),
        followup_number=0,
        topic=result.get("topic"),
    )


@router.post("/{thread_id}/answer", response_model=AnswerOut)
def answer(thread_id: str, body: AnswerIn, session: dict = Depends(owned_session), user: dict = Depends(current_user), spend=Depends(ai_budget)):
    entry = store.get(thread_id, user["id"], session["id"], KIND)
    if entry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "This round has expired. Start a new question.")

    with entry.lock:
        d = entry.data
        if d["done"]:
            raise HTTPException(status.HTTP_409_CONFLICT, "This round is finished. Start a new question.")

        spend()
        # Same input ui/interview_page.py builds: previous graph state plus the new turn.
        graph_input = {
            **d["state"],
            "question": d["question"],
            "answer": body.answer,
            "followup_number": d["followup_number"],
        }
        graph_result = run_ai(interview_graph.invoke, graph_input)

        evaluation = graph_result.get("evaluation") or {}
        if "error" in evaluation:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(evaluation["error"]))

        turn = TurnOut(
            followup_number=d["followup_number"],
            question=d["question"],
            answer=body.answer,
            score=int(evaluation.get("score", 0)),
            strengths=evaluation.get("strengths", ""),
            weaknesses=evaluation.get("weaknesses", ""),
            ideal_answer=evaluation.get("ideal_answer", ""),
            grounded=bool(evaluation.get("grounded", False)),
            sources=evaluation.get("sources", []),
        )

        d["state"] = graph_result
        next_question = graph_result.get("next_question")
        if next_question:
            d["question"] = next_question
            d["sources"] = graph_result.get("sources", [])
            d["followup_number"] += 1
            nxt = NextOut(question=next_question, sources=d["sources"], followup_number=d["followup_number"])
        else:
            d["done"] = True
            nxt = None

    return AnswerOut(turn=turn, next=nxt, done=nxt is None)
