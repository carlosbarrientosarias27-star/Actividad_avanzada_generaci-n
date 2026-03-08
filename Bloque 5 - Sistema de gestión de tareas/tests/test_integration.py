import http.client
import json
import subprocess
import sys
import time
import unittest
import os

HOST, PORT = "127.0.0.1", 8001
# Usamos un archivo temporal para la base de datos para que persista entre tests
TEST_DB = "test_task_manager.db"

def req(method, path, body=None, token=None):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Aseguramos que el body sea bytes o None
    payload = json.dumps(body).encode() if body else b""
    
    try:
        conn.request(method, path, payload, headers)
        r = conn.getresponse()
        status = r.status
        response_data = r.read()
        
        if status >= 400:
            print(f"\n[DEBUG] {method} {path} devolvió {status}: {response_data.decode()}")
            
        # Manejo robusto para respuestas vacías (como el 204 No Content)
        if not response_data or status == 204:
            return status, {}
            
        return status, json.loads(response_data)
    except Exception as e:
        return 500, {"error": str(e)}

class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Limpiamos base de datos previa si existe
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
            
        # Iniciamos el proceso del servidor con variables de entorno controladas
        cls.proc = subprocess.Popen(
            [sys.executable, "main.py"],
            env={
                **os.environ, 
                "PORT": str(PORT), 
                "DATABASE_URL": TEST_DB, 
                "SECRET_KEY": "test-key-123"
            },
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Espera activa hasta que el servidor responda (máximo 5 segundos)
        for _ in range(50):
            try:
                conn = http.client.HTTPConnection(HOST, PORT)
                conn.request("GET", "/health_check_or_fake") # Intento de conexión
                break
            except ConnectionRefusedError:
                time.sleep(0.1)
        else:
            cls.proc.terminate()
            raise RuntimeError("El servidor no arrancó a tiempo para las pruebas")

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait() # Esperamos a que el proceso se cierre
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB) # Limpiamos el archivo temporal

    def test_01_register(self):
        status, body = req("POST", "/register", {"username": "alice", "email": "a@a.com", "password": "secret123"})
        self.assertEqual(status, 201)
        self.assertEqual(body.get("username"), "alice")

    def test_02_register_duplicate(self):
        # Este test ahora funcionará porque la DB persiste entre llamadas
        req("POST", "/register", {"username": "bob", "email": "b@b.com", "password": "secret"})
        status, _ = req("POST", "/register", {"username": "bob", "email": "b@b.com", "password": "secret"})
        self.assertEqual(status, 409)

    def test_03_login(self):
        status, body = req("POST", "/login", {"username": "alice", "password": "secret123"})
        self.assertEqual(status, 200)
        self.assertIn("access_token", body)

    def test_04_task_crud(self):
        # Obtenemos token
        _, login_body = req("POST", "/login", {"username": "alice", "password": "secret123"})
        token = login_body["access_token"]
        
        # 1. Create
        s, task = req("POST", "/tasks", {"title": "Buy milk", "description": "2% fat"}, token)
        self.assertEqual(s, 201)
        self.assertIn("id", task)
        tid = task["id"]
        
        # 2. Read
        s, task_read = req("GET", f"/tasks/{tid}", token=token)
        self.assertEqual(s, 200)
        self.assertEqual(task_read["title"], "Buy milk")
        
        # 3. Update
        s, task_upd = req("PUT", f"/tasks/{tid}", {"status": "done"}, token)
        self.assertEqual(s, 200)
        self.assertEqual(task_upd["status"], "done")
        
        # 4. Delete
        s, _ = req("DELETE", f"/tasks/{tid}", token=token)
        self.assertEqual(s, 204)

    def test_05_unauthorized(self):
        status, _ = req("GET", "/tasks")
        self.assertEqual(status, 401)