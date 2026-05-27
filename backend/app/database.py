import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = os.getenv("VALORA_DB_PATH") or str(Path(__file__).parent.parent / "valora.db")
CONN: Optional[sqlite3.Connection] = None


def _ensure_connection() -> sqlite3.Connection:
    global CONN, DB_PATH
    if CONN is None:
        uri = DB_PATH == ":memory:" or DB_PATH.startswith("file:")
        CONN = sqlite3.connect(DB_PATH, check_same_thread=False, uri=uri)
        CONN.row_factory = sqlite3.Row
        CONN.execute("PRAGMA foreign_keys = ON")
        _initialize_schema(CONN)
    return CONN


def init_db(path: Optional[str] = None) -> sqlite3.Connection:
    global DB_PATH, CONN
    if path:
        DB_PATH = path
    if CONN is not None:
        CONN.close()
        CONN = None
    return _ensure_connection()


def _initialize_schema(conn: sqlite3.Connection) -> None:
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                location TEXT NOT NULL,
                price REAL NOT NULL,
                property_type TEXT NOT NULL,
                category TEXT NOT NULL,
                contact_phone TEXT NOT NULL,
                contact_email TEXT NOT NULL,
                num_bedrooms INTEGER,
                num_bathrooms INTEGER,
                area_sqm REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(owner_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_properties_category ON properties(category)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_properties_type ON properties(property_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(location)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_properties_price ON properties(price)")


def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def _row_to_user(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    return {
        "id": row["id"],
        "email": row["email"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "hashed_password": row["hashed_password"],
        "created_at": _parse_datetime(row["created_at"]),
    }


def _row_to_property(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "owner_id": row["owner_id"],
        "title": row["title"],
        "description": row["description"],
        "location": row["location"],
        "price": row["price"],
        "property_type": row["property_type"],
        "category": row["category"],
        "contact_phone": row["contact_phone"],
        "contact_email": row["contact_email"],
        "num_bedrooms": row["num_bedrooms"],
        "num_bathrooms": row["num_bathrooms"],
        "area_sqm": row["area_sqm"],
        "created_at": _parse_datetime(row["created_at"]),
        "updated_at": _parse_datetime(row["updated_at"]),
    }


def create_user(
    email: str,
    first_name: str,
    last_name: str,
    hashed_password: str,
    import os
    import sqlite3
    from datetime import datetime
    from pathlib import Path
    from typing import Any, Dict, List, Optional
        sql += " ORDER BY price ASC"
    elif sort_by == "price-desc":
        sql += " ORDER BY price DESC"
    else:
        sql += " ORDER BY datetime(created_at) DESC"

    sql += " LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    cursor = conn.execute(sql, tuple(params))
    return [_row_to_property(row) for row in cursor.fetchall()]
