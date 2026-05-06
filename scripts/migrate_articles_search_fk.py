"""
One-time migration for the `articles` table.

Rebuilds the table so `articles.search_id` can reference `searches._id`.
Existing article rows are preserved and `search_id` is left NULL for now.
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def _table_has_column(
    conn: sqlite3.Connection, table_name: str, column_name: str
) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(row[1] == column_name for row in rows)


def migrate(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = OFF;")
        conn.execute("BEGIN;")

        if _table_has_column(conn, "articles", "search_id"):
            conn.execute("COMMIT;")
            return

        conn.execute(
            """
            CREATE TABLE articles_new (
                _id INTEGER PRIMARY KEY,
                search_id INTEGER,
                doi TEXT,
                title TEXT,
                megajournal TEXT,
                journal TEXT,
                FOREIGN KEY(search_id) REFERENCES searches(_id)
            );
            """
        )
        conn.execute(
            """
            INSERT INTO articles_new (_id, doi, title, megajournal, journal)
            SELECT _id, doi, title, megajournal, journal
            FROM articles;
            """
        )
        conn.execute("DROP TABLE articles;")
        conn.execute("ALTER TABLE articles_new RENAME TO articles;")
        conn.execute("COMMIT;")
    except Exception:
        conn.execute("ROLLBACK;")
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("db_path", type=Path)
    args = parser.parse_args()
    migrate(db_path=args.db_path.resolve())


if __name__ == "__main__":
    main()
