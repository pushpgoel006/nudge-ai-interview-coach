"""Sections 8 and 9: DSA problem/submit flow and the dashboard numbers."""

import unittest
from unittest.mock import patch

from services.dsa_service import record_attempt
from services.interview_service import record_interview
from services.resume_service import save_review
from tests_api.helpers import ORIGIN, make_session, new_client, register

PROBLEM = {"session_id": "s", "topic": "array", "difficulty": "easy", "slug": "two-sum", "title": "Two Sum", "statement": "Find two numbers.", "source": "leetcode"}


class DsaTests(unittest.TestCase):
    def setUp(self):
        p = patch("api.routes.dsa.dsa_graph")
        self.graph = p.start()
        self.addCleanup(p.stop)

    def problem(self, c, s, **body):
        return c.post(f"/api/sessions/{s['id']}/dsa/problem", json={"topic": "array", "difficulty": "easy", **body}, headers=ORIGIN)

    def test_problem_then_submit(self):
        with new_client() as c:
            register(c, "dsa1@example.com")
            s = make_session(c)
            self.graph.invoke.return_value = PROBLEM
            r = self.problem(c, s)
            self.assertEqual(r.status_code, 200, r.text)
            p = r.json()
            self.assertEqual((p["title"], p["slug"], p["source"]), ("Two Sum", "two-sum", "leetcode"))
            self.assertEqual(self.graph.invoke.call_args.args[0], {"session_id": s["id"], "topic": "array", "difficulty": "easy"})

            self.graph.invoke.return_value = {"evaluation": {"score": 9, "correctness_notes": "Correct.", "complexity_notes": "O(n).", "suggestions": "Add tests."}}
            r = c.post(f"/api/sessions/{s['id']}/dsa/{p['problem_id']}/submit", json={"code": "def f(): pass", "language": "python"}, headers=ORIGIN)
            self.assertEqual(r.status_code, 200, r.text)
            self.assertEqual(r.json()["score"], 9)
            sent = self.graph.invoke.call_args.args[0]
            self.assertEqual((sent["slug"], sent["statement"], sent["code"], sent["language"], sent["session_id"]), ("two-sum", "Find two numbers.", "def f(): pass", "python", s["id"]))

    def test_validation_and_errors(self):
        with new_client() as c:
            register(c, "dsa2@example.com")
            s = make_session(c)
            self.assertEqual(self.problem(c, s, topic="quantum").status_code, 422)
            self.assertEqual(self.problem(c, s, difficulty="insane").status_code, 422)
            self.graph.invoke.return_value = PROBLEM
            p = self.problem(c, s).json()
            url = f"/api/sessions/{s['id']}/dsa/{p['problem_id']}/submit"
            self.assertEqual(c.post(url, json={"code": "x" * 10001}, headers=ORIGIN).status_code, 422)
            self.assertEqual(c.post(url, json={"code": "print(1)", "language": "cobol"}, headers=ORIGIN).status_code, 422)
            self.graph.invoke.return_value = {"evaluation": {"error": "Could not read the review."}}
            self.assertEqual(c.post(url, json={"code": "print(1)"}, headers=ORIGIN).status_code, 422)
            self.assertEqual(c.post(f"/api/sessions/{s['id']}/dsa/nope/submit", json={"code": "print(1)"}, headers=ORIGIN).status_code, 404)

    def test_problem_ids_are_private(self):
        with new_client() as alice, new_client() as bob:
            register(alice, "dsa3a@example.com")
            register(bob, "dsa3b@example.com")
            sa, sb = make_session(alice), make_session(bob)
            self.graph.invoke.return_value = PROBLEM
            p = self.problem(alice, sa).json()
            r = bob.post(f"/api/sessions/{sb['id']}/dsa/{p['problem_id']}/submit", json={"code": "print(1)"}, headers=ORIGIN)
            self.assertEqual(r.status_code, 404)


class DashboardTests(unittest.TestCase):
    def test_empty_dashboard(self):
        with new_client() as c:
            register(c, "dash1@example.com")
            s = make_session(c)
            d = c.get(f"/api/sessions/{s['id']}/dashboard").json()
            self.assertIsNone(d["readiness"])
            self.assertEqual((d["theory_count"], d["dsa_attempts"], d["trend"], d["weakest"]), (0, 0, [], []))

    def test_numbers_match_the_analytics_service(self):
        with new_client() as c:
            register(c, "dash2@example.com")
            s = make_session(c)
            sid = s["id"]
            record_interview(sid, "indexing", "Q1", "A1", 3, "", "", "")
            record_interview(sid, "apis", "Q2", "A2", 9, "", "", "")
            save_review(sid, 80, ["a"], ["b"], "")
            record_attempt(sid, "array", "easy", "two-sum", "Two Sum", "code", "python", 8, "", "", "")
            record_attempt(sid, "array", "easy", "move-zeroes", "Move Zeroes", "code", "python", 6, "", "", "")
            record_interview(sid, "indexing", "Q3", "A3", 5, "", "", "")
            d = c.get(f"/api/sessions/{sid}/dashboard").json()
            self.assertAlmostEqual(d["theory_average"], 17 / 3)
            self.assertEqual(d["resume_fit"], 80)
            self.assertEqual(d["readiness"], round(0.6 * (17 / 3) * 10 + 0.4 * 80))
            self.assertEqual((d["theory_count"], d["dsa_attempts"], d["dsa_average"]), (3, 2, 7.0))
            weakest = d["weakest"][0]
            self.assertEqual((weakest["topic"], weakest["count"]), ("indexing", 2))
            self.assertAlmostEqual(weakest["average_score"], 4.0)
            self.assertEqual(len(d["trend"]), 3)
            self.assertEqual([p["score"] for p in d["dsa_trend"]], [8, 6])
            self.assertEqual({t["topic"]: t["count"] for t in d["by_topic"]}, {"indexing": 2, "apis": 1})
            self.assertEqual(d["dsa_topics"], [{"topic": "array", "average_score": 7.0, "count": 2}])

    def test_recommendation_and_privacy(self):
        with new_client() as alice, new_client() as bob, patch("api.routes.dashboard.generate_recommendation") as rec:
            register(alice, "dash3a@example.com")
            register(bob, "dash3b@example.com")
            s = make_session(alice)
            rec.return_value = {"advice": "Practise B-trees.", "sources": [{"file_name": "n.pdf", "page": 1, "doc_type": "notes"}]}
            r = alice.post(f"/api/sessions/{s['id']}/dashboard/recommendation", json={"topic": "indexing"}, headers=ORIGIN)
            self.assertEqual(r.status_code, 200, r.text)
            rec.assert_called_once_with(s["id"], "indexing")
            self.assertEqual(bob.get(f"/api/sessions/{s['id']}/dashboard").status_code, 404)
            self.assertEqual(bob.post(f"/api/sessions/{s['id']}/dashboard/recommendation", json={"topic": "x"}, headers=ORIGIN).status_code, 404)
            self.assertEqual(alice.post(f"/api/sessions/{s['id']}/dashboard/recommendation", json={"topic": ""}, headers=ORIGIN).status_code, 422)


if __name__ == "__main__":
    unittest.main()
