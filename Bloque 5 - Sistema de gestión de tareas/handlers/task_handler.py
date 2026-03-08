import json
from auth.middleware import require_auth
from models.task import create_task, get_tasks, get_task, update_task, delete_task

@require_auth
def list_tasks(request, send):
    u = request["user"]
    tasks = get_tasks(u["sub"], u["role"])
    send(200, json.dumps(tasks).encode())

@require_auth
def create(request, send):
    u    = request["user"]
    body = request.get("body", {})
    if not body.get("title"):
        return send(400, json.dumps({"error": "title required"}).encode())
    task = create_task(body["title"], body.get("description", ""), u["sub"])
    send(201, json.dumps(task).encode())

@require_auth
def detail(request, send, task_id: int):
    u    = request["user"]
    task = get_task(task_id, u["sub"], u["role"])
    if not task:
        return send(404, json.dumps({"error": "Not found"}).encode())
    send(200, json.dumps(task).encode())

@require_auth
def update(request, send, task_id: int):
    u    = request["user"]
    body = request.get("body", {})
    task = update_task(task_id, u["sub"], u["role"], **body)
    if not task:
        return send(404, json.dumps({"error": "Not found"}).encode())
    send(200, json.dumps(task).encode())

@require_auth
def delete(request, send, task_id: int):
    u = request["user"]
    if not delete_task(task_id, u["sub"], u["role"]):
        return send(404, json.dumps({"error": "Not found"}).encode())
    send(204, b"")