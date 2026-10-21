"""Remove old demo accounts and their data. Previews by default; deletes only with --yes.

    python -m api.cleanup --days 14 --keep you@example.com          # preview
    python -m api.cleanup --days 14 --keep you@example.com --yes    # actually delete

This deletes EVERY account older than the cutoff, including your own, unless its email is passed
with --keep. It uses whatever DATABASE_URL points at, so check that first. The same purge also runs
at API startup when API_ACCOUNT_TTL_DAYS is above 0 (off by default).
"""

import argparse
import os
from urllib.parse import urlparse

from api import usage
from api.data import list_expired_accounts, purge_expired_accounts
from database.db import DATABASE_URL


def _where() -> str:
    if DATABASE_URL.startswith("sqlite"):
        return "local SQLite file " + DATABASE_URL.split(":///")[-1]
    return "database host " + (urlparse(DATABASE_URL.replace("postgresql+psycopg", "postgresql")).hostname or "?")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--days", type=int, required=True)
    parser.add_argument("--keep", action="append", default=[], help="email to keep (repeatable)")
    parser.add_argument("--yes", action="store_true", help="really delete (otherwise preview only)")
    args = parser.parse_args()

    keep = tuple(args.keep) + tuple(e.strip() for e in os.getenv("API_ACCOUNT_KEEP_EMAILS", "").split(",") if e.strip())
    expired = list_expired_accounts(args.days, keep)
    print(f"Target: {_where()}")
    print(f"{len(expired)} account(s) older than {args.days} days (keeping {len(keep)} email(s)):")
    for a in expired:
        print("  ", a["email"], "created", a["created_at"])
    if not args.yes:
        print("Preview only. Nothing was deleted. Re-run with --yes to delete.")
        return
    usage.ensure_table()
    removed = purge_expired_accounts(args.days, keep)
    usage.prune_older_than(3)
    print(f"Deleted {removed} account(s).")


if __name__ == "__main__":
    main()
