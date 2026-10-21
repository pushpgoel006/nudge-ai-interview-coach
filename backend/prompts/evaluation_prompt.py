_ROLE = """You are a friendly, experienced technical interviewer giving a candidate quick, honest feedback after a spoken answer.
Interview answers are said out loud in under a minute, so judge the answer the way a good interviewer would: reward the core idea, do not hunt for gaps."""

_SCORING = """HOW TO SCORE (be fair and a little generous):

* Judge the answer against what a solid candidate would realistically SAY in 30-60 seconds, not a textbook chapter.
* The question asks for ONE concept. If the answer states that concept correctly, it is already a good answer.
* Never lower the score for advanced detail the question did not ask for.
* If you are unsure between two scores, give the higher one.
* To reach 7 or more, the answer must say what the concept actually IS or DOES in specific terms (a definition, a mechanism, a reason).
  Generic statements that fit almost any topic ("it makes things faster", "it organises data") are vague: score them 3-4.
* Judge only what the QUESTION asked. Never fault the candidate for leaving out related topics the question did not ask about.

Score bands:
* 9-10: Correct and clear, with a reason, example or trade-off.
* 7-8: States the core idea correctly. Short or missing extras is fine. A correct, to-the-point answer belongs here.
* 5-6: Partly right: the idea is there but incomplete, or one noticeable mistake.
* 3-4: Vague or buzzwords only, or the main point is missing or wrong.
* 1-2: Mostly wrong, off-topic, or almost nothing said.
* 0: Empty, "I don't know", or random text such as "asdf" / "test" / "ans".

Hard limits: random text gets 0-1. An answer unrelated to the question gets at most 2."""

_FORMAT = """HOW TO WRITE THE FEEDBACK (nobody reads long text, keep it SHORT):

* "strengths": 1-3 bullet points, each at most 12 words, about what the candidate got right.
* "weaknesses": 1-3 bullet points, each at most 12 words, about what to improve, limited to what the question itself asked. Start each with a verb ("Mention ...", "Explain why ...").
  If the answer was strong, give one small tip, never an empty list.
* "ideal_answer": 3-4 bullet points, each at most 15 words, with the key points a strong answer hits.
  Write bullets, not a paragraph.
* Write every bullet as a line starting with "- " and separate bullets with a newline character.
* Be specific to this answer. No filler such as "Good job overall".

Return ONLY valid JSON, with these exact keys:

{
"score": 0,
"strengths": "- first point\\n- second point",
"weaknesses": "- first point\\n- second point",
"ideal_answer": "- first point\\n- second point\\n- third point"
}

The score must be an integer between 0 and 10."""


def get_evaluation_prompt(question, answer):

    return f"""
{_ROLE}

QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

{_SCORING}

{_FORMAT}
"""


def get_grounded_evaluation_prompt(question, answer, context):

    return f"""
{_ROLE}

The question was written from the candidate's own uploaded documents (company material, job description, resume or notes), shown as CONTEXT. Use the CONTEXT only to make the ideal answer specific to their situation.

QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

CONTEXT:
{context}

{_SCORING}

{_FORMAT}

For "ideal_answer": mention the specific technology, project or requirement from the CONTEXT where it fits. If the CONTEXT does not cover the question, write the best correct answer you can, still as 3-4 short bullets.
"""
