import http.client
import json
import subprocess
import sys
import time
import unittest

HOST, PORT = "127.0.0.1", 8001

def req(method, path, body=None, token=None):
    conn = http.client.HTTPConnection(HOST, PORT)
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    payload = json.dumps(body).encode() if body else b""
    conn.request(method, path, payload, headers)
    r = conn.getresponse()
    return r.status, json.loads(r.read())

class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proc = subprocess.Popen(
            [sys.executable, "main.py"],
            env={"PORT": str(PORT), "DATABASE_URL": ":memory:", "SECRET_KEY": "test-key",
                 "PATH": "/usr/bin:/bin"},
        )
        time.sleep(1)  # wait for server

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()

    def test_01_register(self):
        status, body = req("POST", "/register", {"username": "alice", "email": "a@a.com", "password": "secret123"})
        self.assertEqual(status, 201)
        self.assertEqual(body["username"], "alice")

    def test_02_register_duplicate(self):
        req("POST", "/register", {"username": "bob", "email": "b@b.com", "password": "secret"})
        status, _ = req("POST", "/register", {"username": "bob", "email": "b@b.com", "password": "secret"})
        self.assertEqual(status, 409)

    def test_03_login(self):
        status, body = req("POST", "/login", {"username": "alice", "password": "secret123"})
        self.assertEqual(status, 200)
        self.assertIn("access_token", body)

    def test_04_task_crud(self):
        _, login_body = req("POST", "/login", {"username": "alice", "password": "secret123"})
        token = login_body["access_token"]
        # Create
        s, task = req("POST", "/tasks", {"title": "Buy milk"}, token)
        self.assertEqual(s, 201)
        tid = task["id"]
        # Read
        s, task = req("GET", f"/tasks/{tid}", token=token)
        self.assertEqual(s, 200)
        self.assertEqual(task["title"], "Buy milk")
        # Update
        s, task = req("PUT", f"/tasks/{tid}", {"status": "done"}, token)
        self.assertEqual(s, 200)
        self.assertEqual(task["status"], "done")
        # Delete
        s, _ = req("DELETE", f"/tasks/{tid}", token=token)
        self.assertEqual(s, 204)

    def test_05_unauthorized(self):
        status, _ = req("GET", "/tasks")
        self.assertEqual(status, 401)

    def test_06_refresh_token(self):
        _, body = req("POST", "/login", {"username": "alice", "password": "secret123"})
        s, new = req("POST", "/refresh", {"refresh_token": body["refresh_token"]})
        self.assertEqual(s, 200)
        self.assertIn("access_token", new)

if __name__ == "__main__":
    unittest.main(verbosity=2)