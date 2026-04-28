"""Small CLI to test DatabaseClient saving functionality.

Usage:
    python save_score.py --dsn postgresql://user:pass@host:5432/dbname --username alice --score 42 --level 3

If --dsn omitted, uses DATABASE_URL env variable.
"""

from __future__ import annotations

import argparse
import os
import sys
import datetime

from db import DatabaseClient, DatabaseError
from settings import SettingsManager


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dsn", help="Postgres DSN (postgresql://...)", default=os.getenv("DATABASE_URL"))
    p.add_argument("--username", required=True)
    p.add_argument("--score", type=int, required=True)
    p.add_argument("--level", type=int, required=True)
    args = p.parse_args(argv)

    if args.dsn:
        db = DatabaseClient(dsn=args.dsn)
    else:
        db = DatabaseClient.from_settings(SettingsManager().load())
    try:
        try:
            db.ensure_tables()
        except DatabaseError as e:
            print("Schema check warning:", e)
        db.save_session(args.username, args.score, args.level, datetime.datetime.now(datetime.UTC))
        print("Saved session for", args.username)
        top = db.get_top(10)
        print("Top:")
        for r in top:
            print(f"{r['username']}: {r['score']} (lvl {r['level']}) at {r['played_at']}")
    except DatabaseError as e:
        print("Database error:", e)
        return 2
    finally:
        db.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
