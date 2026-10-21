from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from api.ai import run_ai
from api.deps import ai_budget, current_user, owned_session
from api.threads import store
from graphs.dsa_graph import dsa_graph

router = APIRouter(prefix="/sessions/{session_id}/dsa", tags=["dsa"])

KIND = "dsa"

# The same topic slugs and languages the Streamlit page offers (ui/dsa_page.py).
Topic = Literal[
    "array", "hash-table", "two-pointers", "dynamic-programming", "binary-search", "tree", "graph",
    "linked-list", "stack", "greedy", "backtracking", "sorting", "string", "heap-priority-queue", "sliding-window",
]
Language = Literal["python", "javascript", "java", "cpp"]
Difficulty = Literal["easy", "medium", "hard"]


class ProblemIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    topic: Topic
    difficulty: Difficulty


class SubmitIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str = Field(min_length=5, max_length=10000)
    language: Language = "python"


class ProblemOut(BaseModel):
    problem_id: str
    title: str
    slug: str
    statement: str
    source: str
    topic: str
    difficulty: str


class ReviewOut(BaseModel):
    score: int
    correctness_notes: str
    complexity_notes: str
    suggestions: str


@router.post("/problem", response_model=ProblemOut)
def new_problem(body: ProblemIn, session: dict = Depends(owned_session), user: dict = Depends(current_user), spend=Depends(ai_budget)):
    spend()
    # Same call as "New Problem" in ui/dsa_page.py.
    result = run_ai(
        dsa_graph.invoke, {"session_id": session["id"], "topic": body.topic, "difficulty": body.difficulty}
    )
    problem_id = store.create(
        user["id"], session["id"], KIND, {"problem": result, "topic": body.topic, "difficulty": body.difficulty}
    )
    return ProblemOut(
        problem_id=problem_id,
        title=result["title"],
        slug=result["slug"],
        statement=result["statement"],
        source=result.get("source", ""),
        topic=body.topic,
        difficulty=body.difficulty,
    )


@router.post("/{problem_id}/submit", response_model=ReviewOut)
def submit(problem_id: str, body: SubmitIn, session: dict = Depends(owned_session), user: dict = Depends(current_user), spend=Depends(ai_budget)):
    entry = store.get(problem_id, user["id"], session["id"], KIND)
    if entry is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "That problem has expired. Fetch a new one.")

    with entry.lock:
        d = entry.data
        spend()
        # Same input ui/dsa_page.py builds: the stored problem plus the submitted code.
        graph_input = {
            **d["problem"],
            "session_id": session["id"],
            "topic": d["topic"],
            "difficulty": d["difficulty"],
            "code": body.code,
            "language": body.language,
        }
        result = run_ai(dsa_graph.invoke, graph_input)

    evaluation = result.get("evaluation") or {}
    if "error" in evaluation:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(evaluation["error"]))
    return ReviewOut(
        score=int(evaluation.get("score", 0)),
        correctness_notes=evaluation.get("correctness_notes", ""),
        complexity_notes=evaluation.get("complexity_notes", ""),
        suggestions=evaluation.get("suggestions", ""),
    )
