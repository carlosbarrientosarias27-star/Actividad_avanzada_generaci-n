import json
from auth.jwt_handler import decode_token

def _unauthorized(send, message="Unauthorized"):
    body = json.dumps({"error": message}).encode()
    send(401, body)

def require_auth(handler):
    def wrapper(request, send):
        auth = request.get("headers", {}).get("authorization", "")
        if not auth.startswith("Bearer "):
            return _unauthorized(send)
        try:
            payload = decode_token(auth[7:])
            if payload.get("type") != "access":
                raise ValueError("Wrong token type")
            request["user"] = payload
        except ValueError as e:
            return _unauthorized(send, str(e))
        return handler(request, send)
    return wrapper

def require_admin(handler):
    @require_auth
    def wrapper(request, send):
        if request["user"].get("role") != "admin":
            body = json.dumps({"error": "Forbidden"}).encode()
            return send(403, body)
        return handler(request, send)
    return wrapper