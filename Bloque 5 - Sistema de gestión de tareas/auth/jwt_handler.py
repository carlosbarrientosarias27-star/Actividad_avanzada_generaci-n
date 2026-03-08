import hmac, hashlib, base64, json, time
from config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRY_SECONDS, REFRESH_EXPIRY_SECONDS

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _sign(data: str) -> str:
    return _b64url(hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).digest())

def encode_token(payload: dict, expiry: int = JWT_EXPIRY_SECONDS) -> str:
    header = _b64url(json.dumps({"alg": JWT_ALGORITHM, "typ": "JWT"}).encode())
    payload = {**payload, "exp": int(time.time()) + expiry, "iat": int(time.time())}
    body = _b64url(json.dumps(payload).encode())
    sig = _sign(f"{header}.{body}")
    return f"{header}.{body}.{sig}"

def decode_token(token: str) -> dict:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Malformed token")
        header, body, sig = parts
        if sig != _sign(f"{header}.{body}"):
            raise ValueError("Invalid signature")
        payload = json.loads(base64.urlsafe_b64decode(body + "=="))
        if payload.get("exp", 0) < time.time():
            raise ValueError("Token expired")
        return payload
    except Exception as e:
        raise ValueError(str(e))

def encode_refresh(user_id: int) -> str:
    return encode_token({"sub": user_id, "type": "refresh"}, REFRESH_EXPIRY_SECONDS)

def encode_access(user_id: int, role: str) -> str:
    return encode_token({"sub": user_id, "role": role, "type": "access"})