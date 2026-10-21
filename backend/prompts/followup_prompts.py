_FOLLOWUP_STYLE = """FOLLOW-UP STYLE:

* Ask ONE short theory question that a candidate can answer in 2-4 sentences: at most 20 words, a single question mark.
* Never join two questions with "and" (not "Why X, and how does that affect Y?"). Pick the one that matters most.
* Keep it conceptual: "What is ...?", "Why ...?", "What is the difference between ...?". No scenarios with made-up numbers, no system design, no code, no multi-part questions.
* Match the score:
  - score 0-3: go back to a simpler, foundational question on the same concept.
  - score 4-7: ask about the missing or unclear part of the idea.
  - score 8-10: go one step deeper on the same concept (a reason or trade-off), still short and conceptual.
* Return only the question. No preamble."""


def get_followup_prompt(question, answer, score):

    return f"""
You are a friendly technical interviewer.

Original Question:
{question}

Candidate Answer:
{answer}

Score:
{score}/10

{_FOLLOWUP_STYLE}
"""


def get_grounded_followup_prompt(
    context: str,
    original_question: str,
    original_answer: str,
    history: list[dict],
    latest_answer: str,
    score: int,
) -> str:

    history_text = "\n\n".join(
        f"Follow-up {i + 1} question: {turn['question']}\n"
        f"Follow-up {i + 1} answer: {turn['answer']}"
        for i, turn in enumerate(history)
    ) or "(no follow-ups yet)"

    return f"""
You are a friendly technical interviewer running a short follow-up round.

The material below is the candidate's own uploaded documents (company material, job description, resume or notes).
You may use it to stay on topics that matter for their role, but the question itself must be a general theory question.

MATERIAL:
{context}

Original Question:
{original_question}

Original Answer:
{original_answer}

Previous follow-ups in this thread:
{history_text}

Candidate's latest answer:
{latest_answer}

Score of the latest answer:
{score}/10

{_FOLLOWUP_STYLE}

Also:
* Consider the whole thread above, not only the latest answer. If the candidate said something earlier worth
  returning to, you may refer to it briefly.
* Do not repeat a question already asked in this thread.
"""
