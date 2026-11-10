import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dedup_hash TEXT NOT NULL UNIQUE,
    project_name TEXT NOT NULL,
    location TEXT,
    sector TEXT,
    expertise TEXT,
    consultant_type TEXT,
    engagement_period_months TEXT,
    published_date TEXT,
    deadline TEXT,
    related_url TEXT,
    scraped_at TEXT NOT NULL
);
"""


def get_connection(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(SCHEMA)
    conn.commit()


def upsert_notice(conn: sqlite3.Connection, notice: dict) -> bool:
    """Inserts the notice if its dedup_hash is new. Returns True if inserted,
    False if it was already present (duplicate)."""
    try:
        conn.execute(
            """
            INSERT INTO notices (
                dedup_hash, project_name, location, sector, expertise,
                consultant_type, engagement_period_months, published_date,
                deadline, related_url, scraped_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                notice["dedup_hash"],
                notice["project_name"],
                notice["location"],
                notice["sector"],
                notice["expertise"],
                notice["consultant_type"],
                notice["engagement_period_months"],
                notice["published_date"],
                notice["deadline"],
                notice["related_url"],
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
