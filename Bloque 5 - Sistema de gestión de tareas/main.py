import json
import re
import traceback
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
    def log_message(self, *_): pass  # Silenciar logs por defecto de la consola

    def _read_body(self) -> dict:
        """Lee y parsea el cuerpo JSON de la petición."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                raw_data = self.rfile.read(content_length)
                return json.loads(raw_data)
        except (json.JSONDecodeError, ValueError):
            pass
        return {}

    def _send(self, status: int, body_dict: dict):
        """Helper para enviar respuestas JSON."""
        self.last_status = status  # Guardamos el status para el audit logger
        response_body = json.dumps(body_dict).encode("utf-8")
        
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def _handle(self, method: str):
        ip = self.client_address[0]
        path = self.path.split("?")[0]
        self.last_status = 200 # Status por defecto
        
        # 1. Rate Limiting
        if is_rate_limited(ip):
            self._send(429, {"error": "Too many requests"})
            audit.log(None, method, path, 429, ip)
            return

        # 2. Preparar objeto Request
        headers = {k.lower(): v for k, v in self.headers.items()}
        request = {
            "method":  method,
            "path":    path,
            "headers": headers,
            "body":    self._read_body() if method in ("POST", "PUT", "PATCH") else {},
            "user":    None # Se llenará en los handlers si hay auth
        }

        # 3. Enrutamiento
        for m, pattern, handler in ROUTES:
            if m == method:
                match = re.match(pattern, path)
                if match:
                    try:
                        # Extraer parámetros de la URL (ej: IDs)
                        args = [int(g) for g in match.groups()]
                        
                        # Ejecutar el handler
                        handler(request, self._send, *args)
                        
                        # Extraer user_id después de la ejecución para el log
                        user_id = request.get("user", {}).get("sub") if request.get("user") else None
                        audit.log(user_id, method, path, self.last_status, ip)
                        return
                    
                    except Exception as e:
                        print(f"--- SERVER ERROR ---\n{traceback.format_exc()}")
                        if not hasattr(self, '_headers_buffer') or not self.wfile.closed:
                            self._send(500, {"error": "Internal Server Error", "details": str(e)})
                        audit.log(None, method, path, 500, ip)
                        return

        # 4. 404 Not Found
        self._send(404, {"error": "Not found"})
        audit.log(None, method, path, 404, ip)

    # Mapeo de métodos HTTP
    def do_GET(self):    self._handle("GET")
    def do_POST(self):   self._handle("POST")
    def do_PUT(self):    self._handle("PUT")
    def do_DELETE(self): self._handle("DELETE")

if __name__ == "__main__":
    init_db()
    try:
        server = HTTPServer((SERVER_HOST, SERVER_PORT), Handler)
        print(f"🚀 Server running on http://{SERVER_HOST}:{SERVER_PORT}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()