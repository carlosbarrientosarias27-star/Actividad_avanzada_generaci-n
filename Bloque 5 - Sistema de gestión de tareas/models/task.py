from db import get_conn

def create_task(title: str, description: str, owner_id: int) -> dict | None:
    """Crea una tarea y la devuelve. Usa commit para persistir en DB."""
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title, description, owner_id) VALUES (?,?,?)",
            (title, description, owner_id)
        )
        conn.commit() # Vital para guardar el registro
        task_id = cur.lastrowid
    
    # Recuperamos la tarea recién creada para devolver el objeto completo
    return get_task(task_id, owner_id, role="admin") # "admin" aquí permite saltar el check de dueño al leer el recién creado

def get_tasks(owner_id: int, role: str) -> list[dict]:
    """Lista tareas. Si es admin, ve todas; si no, solo las propias."""
    with get_conn() as conn:
        if role == "admin":
            rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE owner_id=? ORDER BY created_at DESC", 
                (owner_id,)
            ).fetchall()
        return [dict(r) for r in rows]

def get_task(task_id: int, owner_id: int, role: str) -> dict | None:
    """Obtiene una tarea específica validando permisos."""
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if not row:
            return None
        
        task = dict(row)
        # Lógica de autorización: solo admin o el dueño pueden verla
        if role != "admin" and task["owner_id"] != owner_id:
            return None
        return task

def update_task(task_id: int, owner_id: int, role: str, **fields) -> dict | None:
    """Actualiza campos permitidos validando que el usuario tenga permiso."""
    # 1. Verificar si la tarea existe y el usuario tiene acceso
    task = get_task(task_id, owner_id, role)
    if not task:
        return None

    # 2. Filtrar solo los campos que permitimos editar
    allowed = {"title", "description", "status"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    
    if not updates:
        return task

    # 3. Construir la consulta dinámica
    set_clause = ", ".join(f"{k}=?" for k in updates)
    values = list(updates.values())
    
    with get_conn() as conn:
        # Para mayor seguridad, el admin puede editar cualquier ID, 
        # pero el usuario normal solo el suyo.
        if role == "admin":
            query = f"UPDATE tasks SET {set_clause}, updated_at=CURRENT_TIMESTAMP WHERE id=?"
            values.append(task_id)
        else:
            query = f"UPDATE tasks SET {set_clause}, updated_at=CURRENT_TIMESTAMP WHERE id=? AND owner_id=?"
            values.extend([task_id, owner_id])
            
        conn.execute(query, values)
        conn.commit() # Confirmar cambios en DB
        
    return get_task(task_id, owner_id, role)

def delete_task(task_id: int, owner_id: int, role: str) -> bool:
    """Elimina una tarea si el usuario tiene permiso."""
    if not get_task(task_id, owner_id, role):
        return False
        
    with get_conn() as conn:
        if role == "admin":
            conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        else:
            conn.execute("DELETE FROM tasks WHERE id=? AND owner_id=?", (task_id, owner_id))
        conn.commit() # Confirmar borrado
    return True