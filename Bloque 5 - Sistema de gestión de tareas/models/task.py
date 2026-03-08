from db import get_conn

def create_task(title: str, description: str, owner_id: int) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title, description, owner_id) VALUES (?,?,?)",
            (title, description, owner_id)
        )
        return get_task(cur.lastrowid, owner_id, role="user")

def get_tasks(owner_id: int, role: str) -> list[dict]:
    with get_conn() as conn:
        if role == "admin":
            rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE owner_id=? ORDER BY created_at DESC", (owner_id,)
            ).fetchall()
        return [dict(r) for r in rows]

def get_task(task_id: int, owner_id: int, role: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not row:
            return None
        task = dict(row)
        if role != "admin" and task["owner_id"] != owner_id:
            return None
        return task

def update_task(task_id: int, owner_id: int, role: str, **fields) -> dict | None:
    task = get_task(task_id, owner_id, role)
    if not task:
        return None
    allowed = {"title", "description", "status"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return task
    set_clause = ", ".join(f"{k}=?" for k in updates)
    values = list(updates.values()) + [task_id]
    with get_conn() as conn:
        conn.execute(
            f"UPDATE tasks SET {set_clause}, updated_at=CURRENT_TIMESTAMP WHERE id=?", values
        )
    return get_task(task_id, owner_id, role)

def delete_task(task_id: int, owner_id: int, role: str) -> bool:
    if not get_task(task_id, owner_id, role):
        return False
    with get_conn() as conn:
        conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    return True