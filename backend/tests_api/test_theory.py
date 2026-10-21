"""Section 7 checks: the theory thread mirrors ui/interview_page.py, with state held server-side."""

import unittest
from unittest.mock import patch

from services.session_service import record_document
from tests_api.helpers import ORIGIN, make_session, new_client, register

SRC = [{"file_name": "notes.pdf", "page": 2, "doc_type": "notes"}]


def evaluation(score=7, **extra):
    return {"score": score, "strengths": "Clear.", "weaknesses": "Shallow.", "ideal_answer": "Ideal.", "grounded": True, "sources": SRC, **extra}


def graph_result(score=7, nxt=None, **extra):
    return {"evaluation": evaluation(score), "next_question": nxt, "sources": SRC, "interview_id": "iv-1", "messages": [], **extra}


def setup_session(client, email):
    register(client, email)
    s = make_session(client)
    record_document(s["id"], "notes.pdf", "", "notes", 1)
    return s


class TheoryTests(unittest.TestCase):
    def setUp(self):
        g = patch("api.routes.theory.generate_grounded_question")
        i = patch("api.routes.theory.interview_graph")
        self.gen = g.start()
        self.graph = i.start()
        self.gen.return_value = {"question": "Explain B-trees.", "topic": "indexing", "sources": SRC}
        self.addCleanup(g.stop)
        self.addCleanup(i.stop)

    def start(self, c, s, **body):
        return c.post(f"/api/sessions/{s['id']}/theory/start", json={"topic": "indexing", "difficulty": "hard", **body}, headers=ORIGIN)

    def answer(self, c, s, thread, text="B-trees keep keys sorted for range scans."):
        return c.post(f"/api/sessions/{s['id']}/theory/{thread}/answer", json={"answer": text}, headers=ORIGIN)

    def test_full_thread_with_followups_mirrors_the_streamlit_state_flow(self):
        with new_client() as c:
            s = setup_session(c, "th1@example.com")
            r = self.start(c, s)
            self.assertEqual(r.status_code, 200, r.text)
            first = r.json()
            self.gen.assert_called_once_with(s["id"], topic="indexing", difficulty="hard")
            self.assertEqual((first["question"], first["followup_number"]), ("Explain B-trees.", 0))

            # turn 0 -> graph asks a follow-up
            self.graph.invoke.return_value = graph_result(7, nxt="Why not a hash index?")
            r = self.answer(c, s, first["thread_id"])
            self.assertEqual(r.status_code, 200, r.text)
            body = r.json()
            self.assertEqual((body["turn"]["score"], body["turn"]["grounded"], body["done"]), (7, True, False))
            self.assertEqual((body["next"]["question"], body["next"]["followup_number"]), ("Why not a hash index?", 1))
            sent = self.graph.invoke.call_args.args[0]
            self.assertEqual((sent["session_id"], sent["topic"], sent["difficulty"]), (s["id"], "indexing", "hard"))
            self.assertEqual((sent["question"], sent["followup_number"]), ("Explain B-trees.", 0))

            # turn 1 -> previous graph result is carried forward, like st.session_state[state_key]
            self.graph.invoke.return_value = graph_result(8, nxt=None)
            r = self.answer(c, s, first["thread_id"], "Hash indexes only help equality lookups.")
            sent = self.graph.invoke.call_args.args[0]
            self.assertEqual(sent["interview_id"], "iv-1")
            self.assertEqual((sent["question"], sent["followup_number"], sent["answer"]), ("Why not a hash index?", 1, "Hash indexes only help equality lookups."))
            self.assertTrue(r.json()["done"])
            self.assertIsNone(r.json()["next"])

            self.assertEqual(self.answer(c, s, first["thread_id"]).status_code, 409)

    def test_failed_evaluation_does_not_advance_the_round(self):
        with new_client() as c:
            s = setup_session(c, "th2@example.com")
            first = self.start(c, s).json()
            self.graph.invoke.return_value = {"evaluation": {"error": "Could not parse the evaluation."}}
            r = self.answer(c, s, first["thread_id"])
            self.assertEqual(r.status_code, 422)
            self.graph.invoke.return_value = graph_result(6, nxt="Next?")
            ok = self.answer(c, s, first["thread_id"])
            self.assertEqual(ok.status_code, 200)
            self.assertEqual(ok.json()["turn"]["followup_number"], 0)

    def test_needs_documents_and_validates_input(self):
        with new_client() as c:
            register(c, "th3@example.com")
            empty = make_session(c)
            self.assertEqual(self.start(c, empty).status_code, 409)
            self.gen.assert_not_called()
            record_document(empty["id"], "n.pdf", "", "notes", 1)
            self.assertEqual(self.start(c, empty, difficulty="impossible").status_code, 422)
            self.assertEqual(self.start(c, empty, topic="x" * 81).status_code, 422)
            first = self.start(c, empty).json()
            self.assertEqual(self.answer(c, empty, first["thread_id"], "x").status_code, 422)
            extra = c.post(f"/api/sessions/{empty['id']}/theory/{first['thread_id']}/answer", json={"answer": "fine answer", "state": {"interview_id": "other"}}, headers=ORIGIN)
            self.assertEqual(extra.status_code, 422)

    def test_threads_are_private_to_user_and_session(self):
        with new_client() as alice, new_client() as bob:
            s = setup_session(alice, "th4a@example.com")
            register(bob, "th4b@example.com")
            other = make_session(bob)
            first = self.start(alice, s).json()
            self.graph.invoke.return_value = graph_result()
            # Bob cannot use Alice's thread id, in her session or in his own.
            self.assertEqual(self.answer(bob, s, first["thread_id"]).status_code, 404)
            self.assertEqual(self.answer(bob, other, first["thread_id"]).status_code, 404)
            # Alice cannot use it against a different session of hers either.
            second = make_session(alice, "Other", "Role")
            self.assertEqual(self.answer(alice, second, first["thread_id"]).status_code, 404)
            self.assertEqual(self.answer(alice, s, "not-a-real-id").status_code, 404)
            self.graph.invoke.assert_not_called()


if __name__ == "__main__":
    unittest.main()
