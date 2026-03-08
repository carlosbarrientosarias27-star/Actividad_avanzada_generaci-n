import json
from models.user import create_user, get_user_by_username
from auth.password import verify_password
from auth.jwt_handler import encode_access, encode_refresh, decode_token
from db import get_conn
import time

def register(request, send):
    body = request.get("body", {})
    username = body.get("username", "").strip()
    email    = body.get("email", "").strip()
    password = body.get("password", "")
    if not all([username, email, password]):
        return send(400, json.dumps({"error": "username, email and password required"}).encode())
    if get_user_by_username(username):
        return send(409, json.dumps({"error": "Username taken"}).encode())
    user = create_user(username, email, password)
    send(201, json.dumps({"id": user["id"], "username": user["username"]}).encode())

def login(request, send):
    body = request.get("body", {})
    user = get_user_by_username(body.get("username", ""))
    if not user or not verify_password(body.get("password", ""), user["password_hash"]):
        return send(401, json.dumps({"error": "Invalid credentials"}).encode())
    access  = encode_access(user["id"], user["role"])
    refresh = encode_refresh(user["id"])
    expires = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time() + 86400 * 7))
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (?,?,?)",
            (user["id"], refresh, expires)
        )
    send(200, json.dumps({"access_token": access, "refresh_token": refresh}).encode())

def refresh(request, send):
    body  = request.get("body", {})
    token = body.get("refresh_token", "")
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise ValueError("Wrong type")
    except ValueError as e:
        return send(401, json.dumps({"error": str(e)}).encode())
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM refresh_tokens WHERE token=?", (token,)
        ).fetchone()
        if not row:
            return send(401, json.dumps({"error": "Token not found or revoked"}).encode())
        conn.execute("DELETE FROM refresh_tokens WHERE token=?", (token,))
        from models.user import get_user_by_id
        user = get_user_by_id(payload["sub"])
        new_access  = encode_access(user["id"], user["role"])
        new_refresh = encode_refresh(user["id"])
        import time as t
        expires = t.strftime("%Y-%m-%d %H:%M:%S", t.gmtime(t.time() + 86400 * 7))
        conn.execute(
            "INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (?,?,?)",
            (user["id"], new_refresh, expires)
        )
    send(200, json.dumps({"access_token": new_access, "refresh_token": new_refresh}).encode())