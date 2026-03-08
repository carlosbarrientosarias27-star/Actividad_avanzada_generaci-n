import sqlite3
from db import get_conn
from auth.password import hash_password

def create_user(username: str, email: str, password: str, role: str = "user") -> dict | None:
    """Crea un nuevo usuario y devuelve sus datos (sin el hash)."""
    try:
        with get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, email, password_hash, role) VALUES (?,?,?,?)",
                (username, email, hash_password(password), role)
            )
            user_id = cur.lastrowid
            conn.commit() # Aseguramos la persistencia
            return get_user_by_id(user_id)
    except sqlite3.IntegrityError:
        # Error si el username o email ya existen
        return None

def get_user_by_id(user_id: int) -> dict | None:
    """Busca un usuario por ID. Excluye el hash de la contraseña por seguridad."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, username, email, role, created_at FROM users WHERE id=?", 
            (user_id,)
        ).fetchone()
        return dict(row) if row else None

def get_user_by_username(username: str, include_password: bool = False) -> dict | None:
    """
    Busca un usuario por nombre. 
    Permite incluir el password_hash solo para procesos de login internos.
    """
    fields = "*" if include_password else "id, username, email, role, created_at"
    with get_conn() as conn:
        row = conn.execute(
            f"SELECT {fields} FROM users WHERE username=?", 
            (username,)
        ).fetchone()
        return dict(row) if row else None

def get_all_users() -> list[dict]:
    """Devuelve la lista de todos los usuarios registrados."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, username, email, role, created_at FROM users"
        ).fetchall()
        return [dict(r) for r in rows]