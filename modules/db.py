from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("BRIGADAS_DATA_DIR", BASE_DIR / "data"))
DB_PATH = Path(os.environ.get("BRIGADAS_DB_PATH", DATA_DIR / "brigadas.db"))


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    _ensure_data_dir()
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA busy_timeout=30000;")
    return conn


def init_db() -> None:
    with closing(get_connection()) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_mca TEXT NOT NULL,
                nombre_mca TEXT NOT NULL,
                brigadas_realizadas INTEGER NOT NULL,
                personas_brigada_1 INTEGER NOT NULL,
                personas_brigada_2 INTEGER NOT NULL,
                region TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_submissions_created_at ON submissions(created_at DESC);"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_submissions_codigo_mca ON submissions(codigo_mca);"
        )
        conn.commit()


def insert_submission(payload: Dict[str, object]) -> int:
    created_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    with closing(get_connection()) as conn:
        cur = conn.execute(
            """
            INSERT INTO submissions (
                codigo_mca,
                nombre_mca,
                brigadas_realizadas,
                personas_brigada_1,
                personas_brigada_2,
                region,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                str(payload["codigo_mca"]).strip(),
                str(payload["nombre_mca"]).strip(),
                int(payload["brigadas_realizadas"]),
                int(payload["personas_brigada_1"]),
                int(payload["personas_brigada_2"]),
                str(payload["region"]).strip(),
                created_at,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)


def count_records() -> int:
    with closing(get_connection()) as conn:
        row = conn.execute("SELECT COUNT(*) AS total FROM submissions;").fetchone()
        return int(row["total"])


def get_recent_records(limit: int = 500) -> List[Dict[str, object]]:
    with closing(get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                created_at,
                codigo_mca,
                nombre_mca,
                brigadas_realizadas,
                personas_brigada_1,
                personas_brigada_2,
                region
            FROM submissions
            ORDER BY id DESC
            LIMIT ?;
            """,
            (int(limit),),
        ).fetchall()
    return [dict(row) for row in rows]


def get_records_for_export() -> List[Dict[str, object]]:
    """Returns all records in the exact order needed for the Excel export."""
    with closing(get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT
                codigo_mca,
                nombre_mca,
                brigadas_realizadas,
                personas_brigada_1,
                personas_brigada_2,
                region
            FROM submissions
            ORDER BY id ASC;
            """
        ).fetchall()
    return [dict(row) for row in rows]


def delete_all_records() -> None:
    with closing(get_connection()) as conn:
        conn.execute("DELETE FROM submissions;")
        conn.commit()
