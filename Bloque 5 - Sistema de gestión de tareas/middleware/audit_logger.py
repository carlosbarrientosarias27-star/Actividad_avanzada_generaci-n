from db import get_conn

def log(user_id, method: str, path: str, status: int, ip: str):
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO audit_logs (user_id, method, path, status, ip) VALUES (?,?,?,?,?)",
                (user_id, method, path, status, ip)
            )
    except Exception:
        pass  # Audit must never crash the request