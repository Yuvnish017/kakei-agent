from __future__ import annotations

import sqlite3
from pathlib import Path

from kakei_agent.db.schema import SCHEMA_SQL


DEFAULT_DB_PATH = Path("data/kakei.db")


def get_connection(
    db_path: Path = DEFAULT_DB_PATH,
) -> sqlite3.Connection:
    """
    Open the SQLite database and initialize its schema.
    """

    db_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(db_path)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    connection.executescript(SCHEMA_SQL)

    connection.commit()

    return connection