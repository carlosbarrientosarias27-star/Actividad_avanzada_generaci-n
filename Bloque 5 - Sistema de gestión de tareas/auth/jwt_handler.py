import hmac
import hashlib
import base64
import json
import time
from config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRY_SECONDS, REFRESH_EXPIRY_SECONDS

def _b64url_encode(data: bytes) -> str:
    """Codifica a Base64 URL sin padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def _b64url_decode(data: str) -> bytes:
    """Decodifica Base64 URL añadiendo el padding necesario."""
    rem = len(data) % 4
    if rem > 0:
        data += "=" * (4 - rem)
    return base64.urlsafe_b64decode(data)

def _get_signature(data: str) -> str:
    """Genera la firma HMAC-SHA256 basándose en la configuración."""
    # Usamos el algoritmo definido en config si es compatible
    digestmod = hashlib.sha256 if JWT_ALGORITHM == "HS256" else hashlib.sha512
    sig_bytes = hmac.new(SECRET_KEY.encode(), data.encode(), digestmod).digest()
    return _b64url_encode(sig_bytes)

def encode_token(payload: dict, expiry: int) -> str:
    """Genera un JWT completo."""
    now = int(time.time())
    header = _b64url_encode(json.dumps({"alg": JWT_ALGORITHM, "typ": "JWT"}).encode())
    
    # Inyectar claims estándar
    full_payload = {
        **payload,
        "iat": now,
        "exp": now + expiry
    }
    
    body = _b64url_encode(json.dumps(full_payload).encode())
    signature = _get_signature(f"{header}.{body}")
    return f"{header}.{body}.{signature}"

def decode_token(token: str, expected_type: str = None) -> dict:
    """
    Decodifica y valida un JWT. 
    Lanza ValueError si falla alguna validación.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Token malformado")

        header_seg, body_seg, sig_seg = parts
        
        # 1. Validar firma usando compare_digest (Previene Timing Attacks)
        expected_sig = _get_signature(f"{header_seg}.{body_seg}")
        if not hmac.compare_digest(sig_seg, expected_sig):
            raise ValueError("Firma inválida")

        # 2. Decodificar Payload
        payload = json.loads(_b64url_decode(body_seg))

        # 3. Validar Expiración
        if payload.get("exp", 0) < time.time():
            raise ValueError("El token ha expirado")

        # 4. Validar Tipo de Token (Access vs Refresh)
        if expected_type and payload.get("type") != expected_type:
            raise ValueError(f"Tipo de token incorrecto: se esperaba {expected_type}")

        return payload
    except Exception as e:
        # En producción es mejor loguear el error real y devolver un mensaje genérico
        raise ValueError(f"Token no válido: {str(e)}")

def encode_access(user_id: int, role: str) -> str:
    """Crea un token de acceso de corta duración."""
    return encode_token(
        {"sub": user_id, "role": role, "type": "access"}, 
        JWT_EXPIRY_SECONDS
    )

def encode_refresh(user_id: int) -> str:
    """Crea un token de actualización de larga duración."""
    return encode_token(
        {"sub": user_id, "type": "refresh"}, 
        REFRESH_EXPIRY_SECONDS
    )