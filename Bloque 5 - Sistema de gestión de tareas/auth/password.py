import hashlib, os, binascii

ITERATIONS = 260_000
HASH_ALG   = "sha256"
SALT_LEN   = 32

def hash_password(plain: str) -> str:
    salt = os.urandom(SALT_LEN)
    dk = hashlib.pbkdf2_hmac(HASH_ALG, plain.encode(), salt, ITERATIONS)
    return f"{ITERATIONS}${binascii.hexlify(salt).decode()}${binascii.hexlify(dk).decode()}"

def verify_password(plain: str, stored: str) -> bool:
    try:
        iters, salt_hex, dk_hex = stored.split("$")
        salt = binascii.unhexlify(salt_hex)
        dk   = hashlib.pbkdf2_hmac(HASH_ALG, plain.encode(), salt, int(iters))
        return hmac.compare_digest(binascii.hexlify(dk).decode(), dk_hex)
    except Exception:
        return False

import hmac  # noqa: E402 — needed for compare_digest