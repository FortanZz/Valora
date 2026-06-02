import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = os.getenv("VALORA_DB_PATH") or str(Path(__file__).parent.parent / "valora.db")
CONN: Optional[sqlite3.Connection] = None


def _ensure_connection() -> sqlite3.Connection:
    global CONN
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


def close_db() -> None:
    global CONN
    if CONN is not None:
        CONN.close()
        CONN = None


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
        conn.execute("CREATE INDEX IF NOT EXISTS idx_properties_created_at ON properties(created_at)")


def _parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value)


def _serialize_datetime(value: datetime) -> str:
    return value.isoformat()


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


def _row_to_property(row: Optional[sqlite3.Row]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
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
    created_at: datetime,
) -> Dict[str, Any]:
    conn = _ensure_connection()
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO users (email, first_name, last_name, hashed_password, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                email,
                first_name,
                last_name,
                hashed_password,
                _serialize_datetime(created_at),
            ),
        )
    user = get_user_by_id(cursor.lastrowid)
    if user is None:
        raise RuntimeError("Failed to create user")
    return user


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    conn = _ensure_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    return _row_to_user(row)


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = _ensure_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    return _row_to_user(row)


def create_property(
    owner_id: int,
    title: str,
    description: Optional[str],
    location: str,
    price: float,
    property_type: str,
    category: str,
    contact_phone: str,
    contact_email: str,
    num_bedrooms: Optional[int],
    num_bathrooms: Optional[int],
    area_sqm: Optional[float],
    created_at: datetime,
    updated_at: datetime,
) -> Dict[str, Any]:
    conn = _ensure_connection()
    with conn:
        cursor = conn.execute(
            """
            INSERT INTO properties (
                owner_id,
                title,
                description,
                location,
                price,
                property_type,
                category,
                contact_phone,
                contact_email,
                num_bedrooms,
                num_bathrooms,
                area_sqm,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                owner_id,
                title,
                description,
                location,
                price,
                property_type,
                category,
                contact_phone,
                contact_email,
                num_bedrooms,
                num_bathrooms,
                area_sqm,
                _serialize_datetime(created_at),
                _serialize_datetime(updated_at),
            ),
        )
    property_item = get_property_by_id(cursor.lastrowid)
    if property_item is None:
        raise RuntimeError("Failed to create property")
    return property_item


def get_property_by_id(property_id: int) -> Optional[Dict[str, Any]]:
    conn = _ensure_connection()
    row = conn.execute(
        "SELECT * FROM properties WHERE id = ?",
        (property_id,),
    ).fetchone()
    return _row_to_property(row)


def get_properties_by_owner(owner_id: int) -> List[Dict[str, Any]]:
    conn = _ensure_connection()
    rows = conn.execute(
        """
        SELECT * FROM properties
        WHERE owner_id = ?
        ORDER BY datetime(created_at) DESC, id DESC
        """,
        (owner_id,),
    ).fetchall()
    return [item for row in rows if (item := _row_to_property(row)) is not None]


def update_property(
    property_id: int,
    updates: Dict[str, Any],
    updated_at: datetime,
) -> Optional[Dict[str, Any]]:
    conn = _ensure_connection()
    allowed_fields = {
        "title",
        "description",
        "location",
        "price",
        "contact_phone",
        "contact_email",
        "num_bedrooms",
        "num_bathrooms",
        "area_sqm",
    }
    update_values = {
        key: value
        for key, value in updates.items()
        if key in allowed_fields
    }
    update_values["updated_at"] = _serialize_datetime(updated_at)

    assignments = ", ".join(f"{field} = ?" for field in update_values)
    params = list(update_values.values())
    params.append(property_id)

    with conn:
        conn.execute(
            f"UPDATE properties SET {assignments} WHERE id = ?",
            tuple(params),
        )
    return get_property_by_id(property_id)


def delete_property(property_id: int) -> None:
    conn = _ensure_connection()
    with conn:
        conn.execute(
            "DELETE FROM properties WHERE id = ?",
            (property_id,),
        )


def _property_search_clauses(
    query: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    property_type: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[List[str], List[Any]]:
    clauses = []
    params: List[Any] = []

    if search:
        clauses.append("LOWER(location) LIKE ?")
        params.append(f"%{search.strip().lower()}%")

    if query:
        like_query = f"%{query.strip()}%"
        clauses.append("(title LIKE ? OR description LIKE ? OR location LIKE ?)")
        params.extend([like_query, like_query, like_query])
    if min_price is not None:
        clauses.append("price >= ?")
        params.append(min_price)
    if max_price is not None:
        clauses.append("price <= ?")
        params.append(max_price)
    if property_type:
        clauses.append("property_type = ?")
        params.append(property_type)
    if category:
        clauses.append("category = ?")
        params.append(category)
    if location:
        clauses.append("location LIKE ?")
        params.append(f"%{location.strip()}%")

    return clauses, params


def count_properties(
    query: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    property_type: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
) -> int:
    conn = _ensure_connection()
    clauses, params = _property_search_clauses(
        query=query,
        min_price=min_price,
        max_price=max_price,
        property_type=property_type,
        category=category,
        location=location,
        search=search,
    )

    sql = "SELECT COUNT(*) FROM properties"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)

    row = conn.execute(sql, tuple(params)).fetchone()
    return int(row[0]) if row else 0


def search_properties(
    query: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    property_type: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    sort_by: str = "newest",
) -> List[Dict[str, Any]]:
    conn = _ensure_connection()
    clauses, params = _property_search_clauses(
        query=query,
        min_price=min_price,
        max_price=max_price,
        property_type=property_type,
        category=category,
        location=location,
        search=search,
    )

    sql = "SELECT * FROM properties"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)

    if sort_by == "price-asc":
        sql += " ORDER BY price ASC, datetime(created_at) DESC"
    elif sort_by == "price-desc":
        sql += " ORDER BY price DESC, datetime(created_at) DESC"
    else:
        sql += " ORDER BY datetime(created_at) DESC, id DESC"

    sql += " LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    rows = conn.execute(sql, tuple(params)).fetchall()
    return [item for row in rows if (item := _row_to_property(row)) is not None]
