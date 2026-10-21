import random

_STYLE = """QUESTION STYLE (this matters):

* Ask a THEORY question: a concept the candidate can explain out loud in 2-4 sentences.
* Use forms like: "What is ...?", "Explain how ... works.", "What is the difference between X and Y?",
  "Why do we use ...?", "When would you use X instead of Y?"
* ONE question about ONE concept. No multi-part questions ("and also ...").
* Do NOT ask for a system design, an architecture, a debugging case, a long scenario, or anything with
  made-up numbers or scale ("2M requests a day", "design for 10 regions").
* Do NOT ask for code. Do NOT ask something only an expert with years of niche experience could answer.
* Plain wording. At most 2 short lines. Return only the question, with no preamble or explanation."""

_DIFFICULTY = """Difficulty guide:
* easy   -> a definition or "what is / what does" question.
* medium -> explain how or why something works, or compare two related concepts.
* hard   -> still ONE concept, but ask for the trade-off or the reason behind it ("Why is X preferred over Y when ...?")."""


_ANGLES = {
    "easy": ["a definition (\"What is ...?\")", "what problem it solves", "why it is used"],
    "medium": ["how it works", "the difference between it and a closely related concept", "when you would use it"],
    "hard": ["a trade-off or limitation", "why it is preferred over an alternative in a specific situation", "what goes wrong if it is misused"],
}


def _variety_hint(topic: str | None, difficulty: str) -> str:
    # The model tends to ask the same question every time; a random pick keeps practice varied.
    angle = random.choice(_ANGLES.get(difficulty, _ANGLES["medium"]))
    if topic:
        return f"Angle for this question: ask about {angle}."
    rank = random.randint(1, 5)
    return (
        "Silently rank the technologies and skills in the material by importance for the role, and choose number "
        f"{rank} (or the last one if there are fewer). Do NOT write the ranking out. Angle: ask about {angle}."
    )


def get_question_prompt(jd):

    return f"""
You are a friendly technical interviewer.

Read the job description and pick ONE technology or concept it asks for. Ask one theory question about it.

{_STYLE}

Job Description:
{jd}
"""


def get_grounded_question_prompt(context: str, topic: str | None, difficulty: str) -> str:

    topic_line = (
        f"Ask about this topic: {topic}."
        if topic
        else "Pick one technology or concept that appears in the material below."
    )

    return f"""
You are a friendly technical interviewer preparing a candidate for a real interview.

The material below is the candidate's own uploaded documents (company material, job description, resume or notes).
Use it only to choose WHICH concept to ask about: take a technology or skill that really appears in it,
then ask a general theory question about that concept.
Do not ask about the candidate's personal projects or numbers; ask about the underlying concept.

{topic_line}

Difficulty: {difficulty}.

{_DIFFICULTY}

{_variety_hint(topic, difficulty)}

{_STYLE}

Material:
{context}
"""
