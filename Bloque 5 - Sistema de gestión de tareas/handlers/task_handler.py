# Eliminamos 'import json' porque ya no es necesario aquí
from auth.middleware import require_auth
from models.task import create_task, get_tasks, get_task, update_task, delete_task

@require_auth
def list_tasks(request, send):
    """Lista las tareas del usuario autenticado."""
    u = request["user"]
    tasks = get_tasks(u["sub"], u["role"])
    # Enviamos la lista directamente como objeto
    send(200, tasks)

@require_auth
def create(request, send):
    """Crea una nueva tarea."""
    u    = request["user"]
    body = request.get("body", {})
    
    if not body.get("title"):
        return send(400, {"error": "title required"})
        
    task = create_task(body["title"], body.get("description", ""), u["sub"])
    send(201, task)

@require_auth
def detail(request, send, task_id: int):
    """Obtiene los detalles de una tarea específica."""
    u    = request["user"]
    task = get_task(task_id, u["sub"], u["role"])
    
    if not task:
        return send(404, {"error": "Task not found"})
        
    send(200, task)

@require_auth
def update(request, send, task_id: int):
    """Actualiza una tarea existente."""
    u    = request["user"]
    body = request.get("body", {})
    
    task = update_task(task_id, u["sub"], u["role"], **body)
    if not task:
        return send(404, {"error": "Task not found or access denied"})
        
    send(200, task)

@require_auth
def delete(request, send, task_id: int):
    """Elimina una tarea."""
    u = request["user"]
    
    if not delete_task(task_id, u["sub"], u["role"]):
        return send(404, {"error": "Task not found or access denied"})
        
    # 204 No Content no lleva cuerpo
    send(204, {})