from typing import TypedDict

from langchain_core.documents import Document
from langgraph.graph import StateGraph, START, END

from rag.retriever import get_retriever, load_vector_store
from rag.generator import generate_answer
from rag.grader import filter_relevant_documents
from rag.citations import build_sources
from rag.query_rewriter import rewrite_query
from rag.query_decomposer import decompose_question


RETRIEVE_K = 10
SUB_QUESTION_K = 6
CONTEXT_CAP = 14  # most passages handed to the answer step
MAX_RETRIES = 2


class GraphState(TypedDict):
    question: str
    original_question: str
    session_id: str
    documents: list[Document]
    relevant_documents: list[Document]
    grade: str
    sources: list[dict]
    answer: str
    retry_count: int
    sub_questions: list[str]


def retriever_node(state: GraphState):
    print(">>> RETRIEVER NODE")

    state["retry_count"] = state.get("retry_count", 0)

    # k=10 (split across the session's documents) so a comparison can see both sides.
    retriever = get_retriever(state["session_id"], k=RETRIEVE_K)

    documents = retriever.invoke(
        state["question"]
    )

    print("Retrieved:", len(documents))

    state["documents"] = documents

    return state


def grader_node(state: GraphState):
    print(">>> GRADER NODE")

    relevant_documents, grade = filter_relevant_documents(
        state["question"],
        state["documents"],
    )

    print("Grade:", grade)

    # If the strict check dropped everything on the final attempt, answer from what was retrieved
    # instead of giving up; the answer prompt still says so when the context is really unrelated.
    if not relevant_documents and state["documents"] and state.get("retry_count", 0) >= MAX_RETRIES:
        relevant_documents = state["documents"]
        grade = "fallback: using retrieved passages"

    state["relevant_documents"] = relevant_documents
    state["grade"] = grade

    return state


def generate_node(state: GraphState):
    print(">>> GENERATE NODE")

    documents = with_background(state["session_id"], state["relevant_documents"])

    # Answer the user's ORIGINAL question; the retry step may have rewritten state["question"].
    answer = generate_answer(
        state.get("original_question") or state["question"],
        documents,
    )

    print("Generation finished")

    state["answer"] = answer
    state["sources"] = build_sources(documents)

    return state


def with_background(session_id: str, relevant: list[Document]) -> list[Document]:
    """The relevant passages first, then the rest of the session's documents (resume, job description,
    company material, notes), so the model can connect them. Capped to keep the prompt small."""
    try:
        found = load_vector_store().get(
            where={"session_id": session_id}, include=["metadatas", "documents"]
        )
    except Exception:
        return relevant

    seen = {document.page_content for document in relevant}
    extra = []
    for content, metadata in zip(found.get("documents", []), found.get("metadatas", [])):
        if content and content not in seen:
            seen.add(content)
            extra.append(Document(page_content=content, metadata=metadata or {}))

    extra.sort(key=lambda d: (d.metadata.get("doc_type") or "", d.metadata.get("file_name") or "", d.metadata.get("page", 0)))
    return list(relevant) + extra[: max(0, CONTEXT_CAP - len(relevant))]


def not_found_node(state: GraphState):
    print(">>> NOT FOUND NODE")

    state["answer"] = (
        "I couldn't find that information in the uploaded documents."
    )
    state["sources"] = []

    return state


def no_documents_node(state: GraphState):
    print(">>> NO DOCUMENTS NODE")

    state["answer"] = (
        "No documents have been indexed in this prep session yet. "
        "Upload a PDF in the sidebar and press Process Documents."
    )
    state["sources"] = []

    return state


def rewrite_and_retry_node(state: GraphState):
    print(">>> REWRITE NODE (retry", state.get("retry_count", 0) + 1, ")")

    new_question = rewrite_query(state["question"])

    print("Rewritten query:", new_question)

    state["question"] = new_question
    state["retry_count"] = state.get("retry_count", 0) + 1

    return state


def decompose_node(state: GraphState):
    print(">>> DECOMPOSE NODE")

    state["original_question"] = state["question"]

    sub_questions = decompose_question(state["question"])

    print("Sub-questions:", len(sub_questions))

    state["sub_questions"] = sub_questions

    return state


def multi_retrieve_node(state: GraphState):
    print(">>> MULTI-RETRIEVE NODE")

    all_relevant = []
    for sub_q in state["sub_questions"]:
        retriever = get_retriever(state["session_id"], k=SUB_QUESTION_K)
        docs = retriever.invoke(sub_q)
        relevant, _ = filter_relevant_documents(sub_q, docs)
        all_relevant.extend(relevant)

    seen = set()
    deduped = []
    for doc in all_relevant:
        key = (doc.metadata.get("file_name"), doc.metadata.get("page"))
        if key not in seen:
            seen.add(key)
            deduped.append(doc)

    state["relevant_documents"] = deduped
    state["documents"] = deduped

    return state


def route_after_retriever(state: GraphState):
    if not state["documents"]:
        return "no_documents"

    return "grader"


def route_after_grader(state: GraphState):
    if state["relevant_documents"]:
        return "generate"

    if state.get("retry_count", 0) < MAX_RETRIES:
        return "retry"

    return "not_found"


def route_after_decompose(state: GraphState):
    if len(state["sub_questions"]) > 1:
        return "multi_retrieve"
    return "retrieve"


graph = StateGraph(GraphState)

graph.add_node(
    "retrieve",
    retriever_node,
)

graph.add_node(
    "grader",
    grader_node,
)

graph.add_node(
    "generate",
    generate_node,
)

graph.add_node(
    "not_found",
    not_found_node,
)

graph.add_node(
    "no_documents",
    no_documents_node,
)

graph.add_node(
    "retry",
    rewrite_and_retry_node,
)

graph.add_node(
    "decompose",
    decompose_node,
)

graph.add_node(
    "multi_retrieve",
    multi_retrieve_node,
)

graph.add_edge(
    START,
    "decompose",
)

graph.add_conditional_edges(
    "decompose",
    route_after_decompose,
    {
        "retrieve": "retrieve",
        "multi_retrieve": "multi_retrieve",
    },
)

graph.add_conditional_edges(
    "retrieve",
    route_after_retriever,
    {
        "grader": "grader",
        "no_documents": "no_documents",
    },
)

graph.add_conditional_edges(
    "grader",
    route_after_grader,
    {
        "generate": "generate",
        "retry": "retry",
        "not_found": "not_found",
    },
)

graph.add_conditional_edges(
    "multi_retrieve",
    route_after_grader,
    {
        "generate": "generate",
        "retry": "retry",
        "not_found": "not_found",
    },
)

graph.add_edge(
    "retry",
    "retrieve",
)

graph.add_edge(
    "generate",
    END,
)

graph.add_edge(
    "not_found",
    END,
)

graph.add_edge(
    "no_documents",
    END,
)

rag_graph = graph.compile()
