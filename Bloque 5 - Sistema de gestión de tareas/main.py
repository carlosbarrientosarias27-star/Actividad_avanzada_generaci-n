import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

from config import SERVER_HOST, SERVER_PORT
from db import init_db
from middleware.rate_limiter import is_rate_limited
import middleware.audit_logger as audit
from handlers.auth_handler import register, login, refresh
from handlers.task_handler import list_tasks, create, detail, update, delete

ROUTES = [
    ("POST",   r"^/register$",        register),
    ("POST",   r"^/login$",           login),
    ("POST",   r"^/refresh$",         refresh),
    ("GET",    r"^/tasks$",           list_tasks),
    ("POST",   r"^/tasks$",           create),
    ("GET",    r"^/tasks/(\d+)$",     detail),
    ("PUT",    r"^/tasks/(\d+)$",     update),
    ("DELETE", r"^/tasks/(\d+)$",     delete),
]

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass  # Silence default log

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length:
            try:
                return json.loads(self.rfile.read(length))
            except json.JSONDecodeError:
                return {}
        return {}

    def _send(self, status: int, body: bytes):
        self._response_status = status
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle(self, method: str):
        ip = self.client_address[0]
        path = self.path.split("?")[0]
        self._response_status = 500
        user_id = None

        if is_rate_limited(ip):
            self._send(429, json.dumps({"error": "Too many requests"}).encode())
            audit.log(None, method, path, 429, ip)
            return

        headers = {k.lower(): v for k, v in self.headers.items()}
        request = {
            "method":  method,
            "path":    path,
            "headers": headers,
            "body":    self._read_body() if method in ("POST", "PUT", "PATCH") else {},
        }

        for m, pattern, handler in ROUTES:
            if m != method:
                continue
            match = re.match(pattern, path)
            if match:
                groups = [int(g) for g in match.groups()]
                try:
                    handler(request, self._send, *groups)
                    user_id = request.get("user", {}).get("sub")
                except Exception as e:
                    self._send(500, json.dumps({"error": "Internal server error"}).encode())
                audit.log(user_id, method, path, self._response_status, ip)
                return

        self._send(404, json.dumps({"error": "Not found"}).encode())
        audit.log(None, method, path, 404, ip)

    do_GET    = lambda self: self._handle("GET")
    do_POST   = lambda self: self._handle("POST")
    do_PUT    = lambda self: self._handle("PUT")
    do_DELETE = lambda self: self._handle("DELETE")

if __name__ == "__main__":
    init_db()
    server = HTTPServer((SERVER_HOST, SERVER_PORT), Handler)
    print(f"Server running on http://{SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()