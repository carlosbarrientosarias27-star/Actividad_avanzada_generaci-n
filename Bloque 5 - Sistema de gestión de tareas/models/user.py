from db import get_conn
from auth.password import hash_password

def create_user(username: str, email: str, password: str, role: str = "user") -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?,?,?,?)",
            (username, email, hash_password(password), role)
        )
        return get_user_by_id(cur.lastrowid)

def get_user_by_id(user_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row) if row else None

def get_user_by_username(username: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        return dict(row) if row else None

def get_all_users() -> list[dict]:
    with get_conn() as conn:
        return [dict(r) for r in conn.execute("SELECT id,username,email,role,created_at FROM users")]