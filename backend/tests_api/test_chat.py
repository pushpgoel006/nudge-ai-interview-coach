"""Section 5 checks: the chat route calls rag_graph the way the Streamlit UI does."""

import unittest
from unittest.mock import patch

from tests_api.helpers import ORIGIN, make_session, new_client, register

GRAPH_RESULT = {
    "answer": "You are missing Kubernetes.",
    "sources": [{"file_name": "job-description.pdf", "page": 1, "doc_type": "jd"}],
    "documents": [object(), object(), object()],
    "relevant_documents": [object()],
    "retry_count": 1,
    "sub_questions": ["What does the JD require?", "What does the resume show?"],
}


def with_docs(client, session_id):
    """Mark the session as having a document without running real indexing."""
    from services.session_service import record_document

    record_document(session_id, "jd.pdf", "", "jd", 1)


class ChatTests(unittest.TestCase):
    def test_passes_question_and_session_id_and_shapes_the_result(self):
        with new_client() as c, patch("api.routes.chat.rag_graph") as graph:
            graph.invoke.return_value = GRAPH_RESULT
            register(c, "chat1@example.com")
            s = make_session(c)
            with_docs(c, s["id"])
            r = c.post(f"/api/sessions/{s['id']}/chat", json={"question": "  What is missing?  "}, headers=ORIGIN)
            self.assertEqual(r.status_code, 200, r.text)
            graph.invoke.assert_called_once_with({"question": "What is missing?", "session_id": s["id"]})
            body = r.json()
            self.assertEqual(body["answer"], "You are missing Kubernetes.")
            self.assertEqual((body["retrieved_count"], body["kept_count"], body["retry_count"]), (3, 1, 1))
            self.assertEqual(body["sources"][0]["page"], 1)
            self.assertEqual(len(body["sub_questions"]), 2)

    def test_no_documents_does_not_spend_an_llm_call(self):
        with new_client() as c, patch("api.routes.chat.rag_graph") as graph:
            register(c, "chat2@example.com")
            s = make_session(c)
            r = c.post(f"/api/sessions/{s['id']}/chat", json={"question": "Anything?"}, headers=ORIGIN)
            self.assertEqual(r.status_code, 409)
            graph.invoke.assert_not_called()

    def test_graph_failure_is_generic_and_hides_details(self):
        with new_client() as c, patch("api.routes.chat.rag_graph") as graph:
            graph.invoke.side_effect = RuntimeError("secret internal detail: gsk_abc123")
            register(c, "chat3@example.com")
            s = make_session(c)
            with_docs(c, s["id"])
            r = c.post(f"/api/sessions/{s['id']}/chat", json={"question": "Hello there"}, headers=ORIGIN)
            self.assertEqual(r.status_code, 502)
            self.assertNotIn("gsk_", r.text)
            self.assertNotIn("secret", r.text)

    def test_validation_and_ownership(self):
        with new_client() as alice, new_client() as bob, patch("api.routes.chat.rag_graph") as graph:
            register(alice, "chat4a@example.com")
            register(bob, "chat4b@example.com")
            s = make_session(alice)
            with_docs(alice, s["id"])
            self.assertEqual(alice.post(f"/api/sessions/{s['id']}/chat", json={"question": "x"}, headers=ORIGIN).status_code, 422)
            self.assertEqual(alice.post(f"/api/sessions/{s['id']}/chat", json={"question": "x" * 1001}, headers=ORIGIN).status_code, 422)
            self.assertEqual(bob.post(f"/api/sessions/{s['id']}/chat", json={"question": "Whose docs?"}, headers=ORIGIN).status_code, 404)
            graph.invoke.assert_not_called()

    def test_requires_login(self):
        with new_client() as c:
            self.assertEqual(c.post("/api/sessions/x/chat", json={"question": "hi there"}, headers=ORIGIN).status_code, 401)


if __name__ == "__main__":
    unittest.main()
