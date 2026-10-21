"""Section 4 checks: upload validation, limits, ownership and deletion.

The indexer and vector store are mocked so these run fast and offline. Real indexing is
exercised by the live smoke test (tests_api/live_smoke.py).
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from tests_api.helpers import ORIGIN, make_session, new_client, pdf_bytes, register


def upload(client, session_id, data, name="resume.pdf", doc_type="resume", content_type="application/pdf"):
    return client.post(
        f"/api/sessions/{session_id}/documents",
        files={"file": (name, data, content_type)},
        data={"doc_type": doc_type},
        headers=ORIGIN,
    )


class DocumentTests(unittest.TestCase):
    def setUp(self):
        p1 = patch("api.routes.documents.index_documents", return_value=3)
        p2 = patch("api.routes.documents.list_indexed_documents", return_value=["resume.pdf"])
        p3 = patch("api.routes.documents.create_vector_store")
        p4 = patch("api.data.load_vector_store")
        p5 = patch("api.routes.documents.UPLOADS_DIR", Path(tempfile.mkdtemp(prefix="nudge_uploads_")))
        self.index = p1.start()
        self.listing = p2.start()
        self.create_store = p3.start()
        self.store = p4.start().return_value
        p5.start()
        self.store.get.return_value = {"ids": ["a", "b", "c"]}
        for p in (p1, p2, p3, p4, p5):
            self.addCleanup(p.stop)

    def test_upload_list_delete_round_trip(self):
        with new_client() as c:
            register(c, "docs1@example.com")
            s = make_session(c)
            r = upload(c, s["id"], pdf_bytes())
            self.assertEqual(r.status_code, 201, r.text)
            doc = r.json()
            self.assertEqual((doc["file_name"], doc["doc_type"], doc["chunk_count"]), ("resume.pdf", "resume", 3))
            self.index.assert_called_once()
            self.assertEqual(self.index.call_args.kwargs["doc_type"], "resume")

            listed = c.get(f"/api/sessions/{s['id']}/documents").json()
            self.assertEqual(len(listed), 1)
            self.assertTrue(listed[0]["indexed"])

            self.assertEqual(c.delete(f"/api/sessions/{s['id']}/documents/{doc['id']}", headers=ORIGIN).status_code, 204)
            self.store.delete.assert_called_once_with(ids=["a", "b", "c"])
            self.assertEqual(c.get(f"/api/sessions/{s['id']}/documents").json(), [])

    def test_rejects_non_pdf_oversize_and_bad_input(self):
        with new_client() as c:
            register(c, "docs2@example.com")
            s = make_session(c)
            self.assertEqual(upload(c, s["id"], b"hello", "notes.txt").status_code, 415)
            self.assertEqual(upload(c, s["id"], b"not really a pdf", "fake.pdf").status_code, 415)
            self.assertEqual(upload(c, s["id"], pdf_bytes(), doc_type="spaceship").status_code, 422)
            self.assertEqual(upload(c, s["id"], b"%PDF-1.4 garbage" + b"x" * 100, "broken.pdf").status_code, 422)
            self.assertEqual(upload(c, s["id"], pdf_bytes(pages=41), "long.pdf").status_code, 413)
            big = pdf_bytes() + b"0" * (5 * 1024 * 1024)
            self.assertEqual(upload(c, s["id"], big, "big.pdf").status_code, 413)
            self.index.assert_not_called()

    def test_path_traversal_name_is_neutralised(self):
        with new_client() as c:
            register(c, "docs3@example.com")
            s = make_session(c)
            r = upload(c, s["id"], pdf_bytes(), "../../etc/passwd.pdf")
            self.assertEqual(r.status_code, 201)
            self.assertEqual(r.json()["file_name"], "passwd.pdf")
            called_path = self.index.call_args.args[0][0]
            self.assertNotIn("..", str(called_path))

    def test_duplicate_name_and_per_session_limit(self):
        with new_client() as c:
            register(c, "docs4@example.com")
            s = make_session(c)
            self.assertEqual(upload(c, s["id"], pdf_bytes(), "a.pdf").status_code, 201)
            self.assertEqual(upload(c, s["id"], pdf_bytes(), "a.pdf").status_code, 409)
            for n in range(4):
                self.assertEqual(upload(c, s["id"], pdf_bytes(), f"f{n}.pdf").status_code, 201)
            self.assertEqual(upload(c, s["id"], pdf_bytes(), "one-too-many.pdf").status_code, 409)

    def test_unreadable_pdf_text_is_a_clean_error(self):
        self.index.side_effect = ValueError("No text could be extracted from the uploaded documents.")
        with new_client() as c:
            register(c, "docs5@example.com")
            s = make_session(c)
            r = upload(c, s["id"], pdf_bytes(), "scan.pdf")
            self.assertEqual(r.status_code, 422)
            self.assertIn("No text", r.json()["detail"])
            self.assertEqual(c.get(f"/api/sessions/{s['id']}/documents").json(), [])

    def test_missing_from_vector_store_is_flagged(self):
        self.listing.return_value = []
        with new_client() as c:
            register(c, "docs6@example.com")
            s = make_session(c)
            upload(c, s["id"], pdf_bytes())
            self.assertFalse(c.get(f"/api/sessions/{s['id']}/documents").json()[0]["indexed"])

    def test_paste_text_indexes_with_matching_metadata(self):
        with new_client() as c:
            register(c, "docs7@example.com")
            s = make_session(c)
            r = c.post(
                f"/api/sessions/{s['id']}/documents/text",
                json={"doc_type": "jd", "name": "", "text": "We need a backend engineer with Python and SQL experience."},
                headers=ORIGIN,
            )
            self.assertEqual(r.status_code, 201, r.text)
            self.assertEqual(r.json()["file_name"], "job-description.txt")
            chunks = self.create_store.call_args.args[0]
            meta = chunks[0].metadata
            self.assertEqual((meta["session_id"], meta["doc_type"], meta["file_name"], meta["page"]), (s["id"], "jd", "job-description.txt", 0))
            too_short = c.post(f"/api/sessions/{s['id']}/documents/text", json={"doc_type": "jd", "text": "hi"}, headers=ORIGIN)
            self.assertEqual(too_short.status_code, 422)

    def test_other_users_cannot_touch_documents(self):
        with new_client() as alice, new_client() as bob:
            register(alice, "docs8a@example.com")
            register(bob, "docs8b@example.com")
            s = make_session(alice)
            doc = upload(alice, s["id"], pdf_bytes()).json()
            self.assertEqual(bob.get(f"/api/sessions/{s['id']}/documents").status_code, 404)
            self.assertEqual(upload(bob, s["id"], pdf_bytes(), "x.pdf").status_code, 404)
            self.assertEqual(bob.delete(f"/api/sessions/{s['id']}/documents/{doc['id']}", headers=ORIGIN).status_code, 404)
            self.assertEqual(len(alice.get(f"/api/sessions/{s['id']}/documents").json()), 1)

    def test_requires_login(self):
        with new_client() as c:
            self.assertEqual(c.get("/api/sessions/x/documents").status_code, 401)


if __name__ == "__main__":
    unittest.main()
