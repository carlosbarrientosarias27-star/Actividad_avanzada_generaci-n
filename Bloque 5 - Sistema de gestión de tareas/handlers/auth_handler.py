import time
from models.user import create_user, get_user_by_username, get_user_by_id
from auth.password import verify_password
from auth.jwt_handler import encode_access, encode_refresh, decode_token
from db import get_conn
from config import REFRESH_EXPIRY_SECONDS

def register(request, send):
    body = request.get("body", {})
    username = str(body.get("username", "")).strip()
    email    = str(body.get("email", "")).strip()
    password = body.get("password", "")

    if not all([username, email, password]):
        return send(400, {"error": "username, email and password required"})

    if get_user_by_username(username):
        return send(409, {"error": "Username taken"})

    user = create_user(username, email, password)
    if not user:
        return send(500, {"error": "Failed to create user"})
        
    send(201, {"id": user["id"], "username": user["username"]})

def login(request, send):
    body = request.get("body", {})
    # Obtenemos el usuario incluyendo el hash para la verificación
    user = get_user_by_username(body.get("username", ""), include_password=True)
    
    if not user or not verify_password(body.get("password", ""), user["password_hash"]):
        return send(401, {"error": "Invalid credentials"})

    access  = encode_access(user["id"], user["role"])
    refresh = encode_refresh(user["id"])
    
    # Calcular expiración basada en config.py
    expires_ts = time.time() + REFRESH_EXPIRY_SECONDS
    expires_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(expires_ts))

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (?,?,?)",
            (user["id"], refresh, expires_str)
        )
        conn.commit() # ¡Crucial para guardar el token!

    send(200, {
        "access_token": access, 
        "refresh_token": refresh,
        "expires_at": expires_str
    })

def refresh(request, send):
    body  = request.get("body", {})
    token = body.get("refresh_token", "")
    
    try:
        # Validar que el token sea de tipo 'refresh'
        payload = decode_token(token, expected_type="refresh")
    except ValueError as e:
        return send(401, {"error": str(e)})

    with get_conn() as conn:
        # 1. Verificar si el token existe en la DB y no ha sido revocado
        row = conn.execute(
            "SELECT * FROM refresh_tokens WHERE token=?", (token,)
        ).fetchone()
        
        if not row:
            return send(401, {"error": "Token not found or revoked"})

        # 2. Rotación de tokens: borrar el usado y generar uno nuevo
        conn.execute("DELETE FROM refresh_tokens WHERE token=?", (token,))
        
        user = get_user_by_id(payload["sub"])
        if not user:
            conn.commit()
            return send(401, {"error": "User no longer exists"})

        new_access  = encode_access(user["id"], user["role"])
        new_refresh = encode_refresh(user["id"])
        
        expires_ts = time.time() + REFRESH_EXPIRY_SECONDS
        expires_str = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(expires_ts))

        conn.execute(
            "INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (?,?,?)",
            (user["id"], new_refresh, expires_str)
        )
        conn.commit() # Guardar la rotación

    send(200, {
        "access_token": new_access, 
        "refresh_token": new_refresh
    })