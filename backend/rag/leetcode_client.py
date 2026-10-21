import random
import re

import requests

from rag.dsa_extra_problems import extend_fallback
from rag.dsa_fallback_problems import FALLBACK_PROBLEMS

extend_fallback(FALLBACK_PROBLEMS)  # more bundled problems per topic for when LeetCode is unreachable

GRAPHQL_URL = "https://leetcode.com/graphql"
TIMEOUT = 8

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0",
}

QUESTION_LIST_QUERY = """
query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
  problemsetQuestionList: questionList(
    categorySlug: $categorySlug
    limit: $limit
    skip: $skip
    filters: $filters
  ) {
    total: totalNum
    questions: data {
      title
      titleSlug
      difficulty
      isPaidOnly
    }
  }
}
"""

QUESTION_DETAIL_QUERY = """
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    title
    titleSlug
    difficulty
    content
  }
}
"""


def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", "", html or "")
    text = text.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _fallback_problem(topic: str, difficulty: str) -> dict:
    entries = FALLBACK_PROBLEMS.get(topic, {}).get(difficulty, [])
    problem = random.choice(entries)
    return {
        "slug": problem["slug"],
        "title": problem["title"],
        "statement": problem["statement"],
        "source": "fallback",
    }


POOL_SIZE = 100


def _list_questions(topic: str, difficulty: str, skip: int, limit: int) -> dict:
    response = requests.post(
        GRAPHQL_URL,
        json={
            "query": QUESTION_LIST_QUERY,
            "variables": {
                "categorySlug": "",
                "skip": skip,
                "limit": limit,
                "filters": {"tags": [topic], "difficulty": difficulty.upper()},
            },
        },
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["data"]["problemsetQuestionList"]


def _fetch_live(topic: str, difficulty: str) -> dict:
    # Ask how many problems exist for this topic and difficulty, then sample a random window of
    # them, so every request can land anywhere in the topic instead of only its first 50 entries.
    try:
        total = int(_list_questions(topic, difficulty, 0, 1).get("total") or 0)
    except Exception:
        total = 0
    skip = random.randint(0, max(0, total - POOL_SIZE)) if total else 0

    questions = _list_questions(topic, difficulty, skip, POOL_SIZE)["questions"]
    questions = [q for q in questions if not q.get("isPaidOnly")]

    if not questions:
        raise ValueError(f"No free LeetCode questions found for {topic}/{difficulty}")

    chosen = random.choice(questions)

    detail_response = requests.post(
        GRAPHQL_URL,
        json={
            "query": QUESTION_DETAIL_QUERY,
            "variables": {"titleSlug": chosen["titleSlug"]},
        },
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    detail_response.raise_for_status()
    question = detail_response.json()["data"]["question"]
    statement = _strip_html(question.get("content"))

    if not statement:
        raise ValueError(f"Empty content for {chosen['titleSlug']} (likely premium-locked)")

    return {
        "slug": question["titleSlug"],
        "title": question["title"],
        "statement": statement,
        "source": "leetcode",
    }


def fetch_problem(topic: str, difficulty: str) -> dict:
    try:
        return _fetch_live(topic, difficulty)
    except Exception as error:
        print(">>> LEETCODE LIVE FETCH FAILED, using fallback:", error)
        return _fallback_problem(topic, difficulty)
