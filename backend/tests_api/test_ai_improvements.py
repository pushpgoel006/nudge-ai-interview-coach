"""Checks for the prompt, pipeline and DSA-bank improvements. Everything is mocked: no LLM, no network."""

import unittest
from unittest.mock import MagicMock, patch

import tests_api  # noqa: F401  (forces the throwaway database before anything imports database.db)
from langchain_core.documents import Document


def doc(text, name="resume.pdf", page=0, kind="resume"):
    return Document(page_content=text, metadata={"file_name": name, "page": page, "doc_type": kind})


class PromptTests(unittest.TestCase):
    def test_evaluation_prompts_ask_for_short_bullets_and_a_fair_score(self):
        from prompts.evaluation_prompt import get_evaluation_prompt, get_grounded_evaluation_prompt

        for prompt in (get_evaluation_prompt("What is an index?", "A lookup structure."),
                       get_grounded_evaluation_prompt("What is an index?", "A lookup structure.", "ctx")):
            self.assertIn("at most 12 words", prompt)
            self.assertIn("at most 15 words", prompt)
            self.assertIn("bullet", prompt.lower())
            self.assertIn('"ideal_answer"', prompt)
            self.assertIn("a little generous", prompt)
            self.assertNotIn("{{", prompt)  # the JSON example must reach the model with single braces
            self.assertIn("States the core idea correctly", prompt)

    def test_question_prompts_ask_for_theory_not_scenarios(self):
        from prompts.question_prompts import get_grounded_question_prompt, get_question_prompt

        for prompt in (get_grounded_question_prompt("material", "indexing", "hard"), get_question_prompt("a jd")):
            self.assertIn("THEORY", prompt)
            self.assertIn("What is", prompt)
            self.assertIn("Do NOT ask for a system design", prompt)
        self.assertIn("indexing", get_grounded_question_prompt("material", "indexing", "easy"))
        self.assertIn("hard", get_grounded_question_prompt("material", None, "hard"))

    def test_question_prompts_vary_so_practice_is_not_repetitive(self):
        from prompts.question_prompts import get_grounded_question_prompt

        no_topic = {get_grounded_question_prompt("material", None, "medium") for _ in range(60)}
        with_topic = {get_grounded_question_prompt("material", "indexing", "hard") for _ in range(60)}
        self.assertGreaterEqual(len(no_topic), 5)
        self.assertGreaterEqual(len(with_topic), 2)

    def test_scoring_rules_penalise_vague_answers_and_stay_on_the_question(self):
        from prompts.evaluation_prompt import get_evaluation_prompt

        prompt = get_evaluation_prompt("What is an index?", "It makes things faster.")
        self.assertIn("vague", prompt)
        self.assertIn("score them 3-4", prompt)
        self.assertIn("Never fault the candidate for leaving out related topics", prompt)

    def test_followups_stay_short_and_conceptual(self):
        from prompts.followup_prompts import get_followup_prompt, get_grounded_followup_prompt

        a = get_followup_prompt("q", "a", 5)
        b = get_grounded_followup_prompt("ctx", "q", "a", [{"question": "f1", "answer": "x"}], "latest", 9)
        for prompt in (a, b):
            self.assertIn("ONE short theory question", prompt)
            self.assertIn("at most 20 words", prompt)
            self.assertIn("Never join two questions", prompt)
            self.assertIn("score 8-10", prompt)
        self.assertIn("f1", b)

    def test_rag_prompt_demands_connection_and_clear_tables(self):
        from prompts.rag_prompts import RAG_PROMPT

        text = RAG_PROMPT.format(context="[resume.pdf | p.1 | resume]\nPython", question="Q?")
        self.assertIn("Connect the dots", text)
        self.assertIn("| Requirement | Evidence | Verdict |", text)
        self.assertIn("(inference)", text)
        self.assertIn("Next step:", text)
        self.assertIn("I couldn't find that information in the uploaded documents.", text)
        self.assertIn("Python", text)


class QuestionCleanupTests(unittest.TestCase):
    def test_keeps_only_the_question_when_the_model_prints_its_working(self):
        from agents.question_generator import _clean_question

        messy = "- REST APIs (Python)\n- Docker\n- Kafka\n\nWhen would you choose FastAPI instead of Flask?"
        self.assertEqual(_clean_question(messy), "When would you choose FastAPI instead of Flask?")
        self.assertEqual(_clean_question('"What is an index?"'), "What is an index?")
        self.assertEqual(_clean_question("What is Docker?"), "What is Docker?")
        self.assertEqual(_clean_question("Explain Docker\nin two lines"), "in two lines")
        self.assertEqual(_clean_question(""), "")


class EvaluatorParsingTests(unittest.TestCase):
    def test_bullets_with_real_newlines_still_parse(self):
        from agents import evaluator

        raw = '```json\n{"score": 8, "strengths": "- clear\n- correct", "weaknesses": "- add an example", "ideal_answer": "- one\n- two"}\n```'
        fake = MagicMock()
        fake.invoke.return_value = MagicMock(content=raw)
        with patch.object(evaluator, "llm", fake):
            result = evaluator.evaluate_answer("Q", "A")
        self.assertEqual(result["score"], 8)
        self.assertEqual(result["strengths"].splitlines(), ["- clear", "- correct"])
        self.assertEqual(result["ideal_answer"].splitlines(), ["- one", "- two"])


class RagPipelineTests(unittest.TestCase):
    def setUp(self):
        import graphs.rag_graph as g

        self.g = g

    def test_context_is_labelled_with_file_page_and_type(self):
        from rag.generator import format_context

        text = format_context([doc("Built REST APIs."), doc("Needs Kubernetes.", name="jd.pdf", page=1, kind="jd")])
        self.assertIn("[resume.pdf | p.1 | resume]\nBuilt REST APIs.", text)
        self.assertIn("[jd.pdf | p.2 | jd]\nNeeds Kubernetes.", text)

    def test_background_adds_the_rest_of_the_session_after_the_relevant_passages(self):
        found = {
            "documents": ["relevant text", "jd text", "notes text"],
            "metadatas": [
                {"file_name": "resume.pdf", "page": 0, "doc_type": "resume"},
                {"file_name": "jd.pdf", "page": 0, "doc_type": "jd"},
                {"file_name": "notes.pdf", "page": 0, "doc_type": "notes"},
            ],
        }
        store = MagicMock()
        store.get.return_value = found
        with patch.object(self.g, "load_vector_store", return_value=store):
            docs = self.g.with_background("s1", [doc("relevant text")])
        self.assertEqual(docs[0].page_content, "relevant text")
        self.assertEqual({d.page_content for d in docs}, {"relevant text", "jd text", "notes text"})
        self.assertEqual(len(docs), 3)  # the relevant passage is not repeated
        store.get.assert_called_once()
        self.assertEqual(store.get.call_args.kwargs["where"], {"session_id": "s1"})

    def test_background_is_capped_and_survives_a_store_error(self):
        many = {"documents": [f"t{i}" for i in range(50)], "metadatas": [{"file_name": "a.pdf", "page": i, "doc_type": "notes"} for i in range(50)]}
        store = MagicMock()
        store.get.return_value = many
        with patch.object(self.g, "load_vector_store", return_value=store):
            self.assertEqual(len(self.g.with_background("s", [doc("r")])), self.g.CONTEXT_CAP)
        with patch.object(self.g, "load_vector_store", side_effect=RuntimeError("offline")):
            relevant = [doc("only")]
            self.assertEqual(self.g.with_background("s", relevant), relevant)

    def test_generation_answers_the_original_question_not_the_rewrite(self):
        state = {
            "question": "rewritten search words",
            "original_question": "Where do I fall short of this role?",
            "session_id": "s",
            "relevant_documents": [doc("x")],
        }
        with patch.object(self.g, "generate_answer", return_value="ANSWER") as gen, patch.object(self.g, "with_background", side_effect=lambda sid, rel: rel):
            out = self.g.generate_node(state)
        self.assertEqual(gen.call_args.args[0], "Where do I fall short of this role?")
        self.assertEqual(out["answer"], "ANSWER")

    def test_decompose_remembers_the_original_question(self):
        with patch.object(self.g, "decompose_question", return_value=["only one"]):
            out = self.g.decompose_node({"question": "What is missing?", "session_id": "s"})
        self.assertEqual(out["original_question"], "What is missing?")

    def test_retrieval_uses_a_wider_net(self):
        retriever = MagicMock()
        retriever.invoke.return_value = [doc("a")]
        with patch.object(self.g, "get_retriever", return_value=retriever) as get:
            self.g.retriever_node({"question": "q", "session_id": "s"})
        self.assertEqual(get.call_args.kwargs["k"], self.g.RETRIEVE_K)
        self.assertGreater(self.g.RETRIEVE_K, 4)

    def test_final_attempt_falls_back_to_retrieved_passages_instead_of_giving_up(self):
        retrieved = [doc("something related")]
        with patch.object(self.g, "filter_relevant_documents", return_value=([], "0/1 relevant")):
            early = self.g.grader_node({"question": "q", "documents": retrieved, "retry_count": 0})
            late = self.g.grader_node({"question": "q", "documents": retrieved, "retry_count": self.g.MAX_RETRIES})
        self.assertEqual(early["relevant_documents"], [])
        self.assertEqual(late["relevant_documents"], retrieved)
        self.assertEqual(self.g.route_after_grader(early), "retry")
        self.assertEqual(self.g.route_after_grader(late), "generate")
        none_at_all = {"relevant_documents": [], "retry_count": self.g.MAX_RETRIES}
        self.assertEqual(self.g.route_after_grader(none_at_all), "not_found")


class DsaBankTests(unittest.TestCase):
    def test_every_topic_and_difficulty_has_several_distinct_problems(self):
        from rag.leetcode_client import FALLBACK_PROBLEMS

        self.assertEqual(len(FALLBACK_PROBLEMS), 15)
        for topic, by_difficulty in FALLBACK_PROBLEMS.items():
            self.assertEqual(set(by_difficulty), {"easy", "medium", "hard"}, topic)
            for difficulty, problems in by_difficulty.items():
                self.assertGreaterEqual(len(problems), 2, f"{topic}/{difficulty}")
                slugs = [p["slug"] for p in problems]
                self.assertEqual(len(slugs), len(set(slugs)), f"duplicate in {topic}/{difficulty}")
        total = sum(len(v) for t in FALLBACK_PROBLEMS.values() for v in t.values())
        self.assertGreaterEqual(total, 120)

    def test_every_problem_is_complete(self):
        from rag.leetcode_client import FALLBACK_PROBLEMS

        seen = {}
        for by_difficulty in FALLBACK_PROBLEMS.values():
            for problems in by_difficulty.values():
                for p in problems:
                    self.assertTrue(p["slug"] and p["title"] and len(p["statement"]) > 60, p["slug"])
                    self.assertEqual(p["slug"], p["slug"].lower())
                    self.assertNotIn(" ", p["slug"])
                    seen.setdefault(p["slug"], p["title"])
                    self.assertEqual(seen[p["slug"]], p["title"])  # one title per slug

    def test_live_fetch_samples_a_random_window_across_the_whole_topic(self):
        import rag.leetcode_client as c

        calls = []

        def fake_post(url, json=None, **_):
            calls.append(json["variables"])
            resp = MagicMock()
            if "titleSlug" in json["variables"]:
                resp.json.return_value = {"data": {"question": {"title": "Word Break", "titleSlug": "word-break", "content": "<p>Given a string s...</p>"}}}
            elif json["variables"]["limit"] == 1:
                resp.json.return_value = {"data": {"problemsetQuestionList": {"total": 400, "questions": [{"titleSlug": "x", "isPaidOnly": False}]}}}
            else:
                resp.json.return_value = {"data": {"problemsetQuestionList": {"total": 400, "questions": [
                    {"title": "Paid", "titleSlug": "paid", "isPaidOnly": True},
                    {"title": "Word Break", "titleSlug": "word-break", "isPaidOnly": False}]}}}
            return resp

        skips = set()
        with patch.object(c.requests, "post", side_effect=fake_post):
            for _ in range(40):
                result = c.fetch_problem("dynamic-programming", "medium")
                self.assertEqual((result["slug"], result["source"]), ("word-break", "leetcode"))
        for variables in calls:
            if "skip" in variables and variables["limit"] == c.POOL_SIZE:
                skips.add(variables["skip"])
                self.assertTrue(0 <= variables["skip"] <= 400 - c.POOL_SIZE)
        self.assertGreater(len(skips), 5)  # it really does move around, not always skip=0

    def test_falls_back_to_the_bundled_bank_when_leetcode_is_unreachable(self):
        import rag.leetcode_client as c

        with patch.object(c.requests, "post", side_effect=ConnectionError("blocked")):
            seen = {c.fetch_problem("graph", "medium")["slug"] for _ in range(40)}
        self.assertTrue(seen)
        self.assertGreaterEqual(len(seen), 2)  # more than one problem to rotate through


if __name__ == "__main__":
    unittest.main()
