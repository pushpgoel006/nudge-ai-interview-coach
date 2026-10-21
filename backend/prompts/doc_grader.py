from langchain_core.prompts import PromptTemplate


GRADER_PROMPT = PromptTemplate.from_template(
    """
You are a lenient relevance checker for an interview-preparation assistant.

Decide whether the passage below could help answer the question, directly or indirectly.

The question may:
- ask for something stated in a document,
- compare or connect documents (resume vs job description vs company material vs notes),
- ask whether a person meets requirements, or what is missing,
- need several passages combined to answer.

Rules:

- Answer ONLY "yes" or "no". No explanation.
- Answer "yes" if the passage is about the same role, person, skills, tools, projects, company or requirements
  the question touches, even if it only supplies part of the picture or one side of a comparison.
- When the question is about fit, gaps or comparing, passages from the resume, job description, company
  material or notes are all useful: answer "yes".
- Answer "no" only if the passage is clearly about something unrelated to the question.

Question:
{question}

Passage:
{context}

Answer:
"""
)
