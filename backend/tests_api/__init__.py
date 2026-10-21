"""Test package setup. This runs before ANY test module is imported, in any order.

It points the database at a throwaway SQLite file *before* `database.db` can be imported,
because that module reads DATABASE_URL (from the environment or .env) at import time. Without
this, a test run could talk to the real database. `helpers` double-checks it below.
"""

import atexit
import os
import shutil
import tempfile

TEST_DB_DIR = tempfile.mkdtemp(prefix="nudge_api_test_")
TEST_DB_URL = "sqlite:///" + os.path.join(TEST_DB_DIR, "test.db").replace("\\", "/")

# Assign, never setdefault: a real DATABASE_URL in the shell must not win.
os.environ["DATABASE_URL"] = TEST_DB_URL
os.environ.pop("DATABASE_URL_UNPOOLED", None)
os.environ["API_SECRET_KEY"] = "test-secret-key-not-for-production"
os.environ["API_ENV"] = "development"
os.environ["API_ALLOWED_ORIGINS"] = "http://localhost:3000"
os.environ.setdefault("GROQ_API_KEY", "test-key-never-used")

atexit.register(lambda: shutil.rmtree(TEST_DB_DIR, ignore_errors=True))
