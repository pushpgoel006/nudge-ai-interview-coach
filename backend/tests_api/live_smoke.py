"""Live smoke test against a RUNNING API (real embeddings, real LLM calls).

Start the API first with throwaway data (see api/README.md), then:
    .venv\\Scripts\\python tests_api/live_smoke.py [base_url] [stage ...]

Stages: docs chat resume theory dsa dashboard   (default: every stage)
Each run registers a fresh test user and cleans up after itself. It makes a handful
of real LLM calls, so do not point it at a production deployment.
"""

import sys
import time
import uuid

import httpx
import pymupdf

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = (sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].startswith("http") else "http://127.0.0.1:8000").rstrip("/")
STAGES = [a for a in sys.argv[1:] if not a.startswith("http")] or ["docs", "chat", "resume", "theory", "dsa", "dashboard"]
ORIGIN = {"Origin": "http://localhost:3000"}

JD = (
    "Backend Engineer at Acme Corp. Requirements: strong Python, REST API design, PostgreSQL and SQL "
    "performance tuning, Docker, Kubernetes for deployment, and on-call ownership of production services. "
    "Nice to have: experience with message queues such as Kafka and with CI/CD pipelines."
)
RESUME = (
    "Alex Rivera. Backend developer, 4 years. Built REST APIs in Python (FastAPI, Flask) serving 2M requests a day. "
    "Designed PostgreSQL schemas and tuned slow queries using indexes and EXPLAIN. Containerised services with Docker "
    "and set up GitHub Actions CI pipelines. Projects: a Kafka consumer for order events, a rate limiter in Redis."
)


def pdf(text: str) -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_textbox(pymupdf.Rect(60, 60, 540, 780), text, fontsize=11)
    return doc.tobytes()


def step(name: str):
    print(f"\n== {name}")


def ok(cond: bool, message: str):
    print(("  PASS " if cond else "  FAIL ") + message)
    if not cond:
        raise SystemExit(1)


def main():
    c = httpx.Client(base_url=BASE + "/api", headers=ORIGIN, timeout=300)
    email = f"smoke-{uuid.uuid4().hex[:8]}@example.test"
    r = c.post("/auth/register", json={"email": email, "password": "smoke-pass-1234", "display_name": "Smoke"})
    ok(r.status_code == 201, f"register ({r.status_code})")
    s = c.post("/sessions", json={"company_name": "Acme Corp", "role": "Backend Engineer"}).json()
    sid = s["id"]
    state: dict = {}

    try:
        if "docs" in STAGES or any(x in STAGES for x in ("chat", "resume", "theory", "dsa", "dashboard")):
            step("documents")
            t = time.time()
            r = c.post(f"/sessions/{sid}/documents", files={"file": ("job-description.pdf", pdf(JD), "application/pdf")}, data={"doc_type": "jd"})
            ok(r.status_code == 201, f"upload JD pdf ({r.status_code}) in {time.time() - t:.1f}s: {r.text[:120]}")
            r = c.post(f"/sessions/{sid}/documents", files={"file": ("resume.pdf", pdf(RESUME), "application/pdf")}, data={"doc_type": "resume"})
            ok(r.status_code == 201, f"upload resume pdf ({r.status_code})")
            docs = c.get(f"/sessions/{sid}/documents").json()
            ok(len(docs) == 2 and all(d["indexed"] for d in docs), f"listed 2 documents, both indexed: {[(d['file_name'], d['chunk_count']) for d in docs]}")

        if "chat" in STAGES:
            step("chat")
            r = c.post(f"/sessions/{sid}/chat", json={"question": "Which required skills in the job description are missing from my resume?"})
            ok(r.status_code == 200, f"chat ({r.status_code})")
            body = r.json()
            print("  answer:", body["answer"][:300].replace("\n", " "))
            # The grader and generator are LLMs, so whether sources are kept varies run to run; only require an answer.
            ok(bool(body["answer"]), f"got an answer; {len(body['sources'])} source(s), retrieved={body['retrieved_count']} kept={body['kept_count']}")

        if "resume" in STAGES:
            step("resume check")
            r = c.post(f"/sessions/{sid}/resume/check")
            ok(r.status_code == 200, f"resume check ({r.status_code}): {r.text[:200]}")
            review = r.json()
            ok(isinstance(review["overall_score"], int), f"fit score {review['overall_score']}, {len(review.get('verdicts', []))} verdicts")
            ok(c.get(f"/sessions/{sid}/resume").json() is not None, "latest review readable")

        if "theory" in STAGES:
            step("theory round")
            r = c.post(f"/sessions/{sid}/theory/start", json={"topic": "PostgreSQL indexing", "difficulty": "medium"})
            ok(r.status_code == 200, f"start ({r.status_code})")
            first = r.json()
            print("  question:", first["question"][:200].replace("\n", " "))
            r = c.post(f"/sessions/{sid}/theory/{first['thread_id']}/answer", json={"answer": "I would use a B-tree index by default because it supports range scans and ordering, and check EXPLAIN ANALYZE before and after."})
            ok(r.status_code == 200, f"answer ({r.status_code}): {r.text[:200]}")
            turn = r.json()
            ok(0 <= turn["turn"]["score"] <= 10, f"score {turn['turn']['score']}/10, grounded={turn['turn']['grounded']}, followup={'yes' if turn['next'] else 'no'}")
            if turn["next"]:
                r = c.post(f"/sessions/{sid}/theory/{first['thread_id']}/answer", json={"answer": "Hash indexes only help equality lookups and were not crash safe in old versions, so I rarely use them."})
                ok(r.status_code == 200, f"follow-up answer ({r.status_code})")

        if "dsa" in STAGES:
            step("dsa round")
            r = c.post(f"/sessions/{sid}/dsa/problem", json={"topic": "array", "difficulty": "easy"})
            ok(r.status_code == 200, f"problem ({r.status_code})")
            problem = r.json()
            print("  problem:", problem["title"], "| source:", problem["source"])
            code = "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i\n"
            r = c.post(f"/sessions/{sid}/dsa/{problem['problem_id']}/submit", json={"code": code, "language": "python"})
            ok(r.status_code == 200, f"submit ({r.status_code}): {r.text[:200]}")
            ok(0 <= r.json()["score"] <= 10, f"score {r.json()['score']}/10")

        if "dashboard" in STAGES:
            step("dashboard")
            r = c.get(f"/sessions/{sid}/dashboard")
            ok(r.status_code == 200, f"dashboard ({r.status_code})")
            d = r.json()
            print("  ", {k: d[k] for k in ("readiness", "theory_average", "resume_fit", "dsa_average")})
            if d["weakest"]:
                r = c.post(f"/sessions/{sid}/dashboard/recommendation", json={"topic": d["weakest"][0]["topic"]})
                ok(r.status_code == 200, f"recommendation ({r.status_code})")
    finally:
        step("cleanup")
        r = c.post("/me/delete", json={"password": "smoke-pass-1234"})
        print("  delete my data:", r.status_code)
        if r.status_code != 204:
            raise SystemExit(1)
    print("\nALL STAGES PASSED")


if __name__ == "__main__":
    main()
