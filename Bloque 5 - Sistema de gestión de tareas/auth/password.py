import hashlib
import os
import hmac
import binascii

# Configuraciones recomendadas por OWASP para PBKDF2-HMAC-SHA256
ITERATIONS = 260_000
HASH_ALG   = "sha256"
SALT_LEN   = 32

def hash_password(plain: str) -> str:
    """
    Genera un hash seguro utilizando PBKDF2.
    Formato: iteraciones$salt_hex$hash_hex
    """
    salt = os.urandom(SALT_LEN)
    dk = hashlib.pbkdf2_hmac(
        HASH_ALG, 
        plain.encode('utf-8'), 
        salt, 
        ITERATIONS
    )
    
    # Convertimos a hex para almacenamiento seguro en DB (TEXT)
    salt_hex = binascii.hexlify(salt).decode()
    dk_hex = binascii.hexlify(dk).decode()
    
    return f"{ITERATIONS}${salt_hex}${dk_hex}"

def verify_password(plain: str, stored: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con el hash almacenado.
    """
    try:
        # 1. Separar y validar el formato almacenado
        parts = stored.split("$")
        if len(parts) != 3:
            return False
            
        iters_str, salt_hex, dk_hex = parts
        
        # 2. Re-generar el hash con la sal y las iteraciones originales
        salt = binascii.unhexlify(salt_hex)
        dk_check = hashlib.pbkdf2_hmac(
            HASH_ALG, 
            plain.encode('utf-8'), 
            salt, 
            int(iters_str)
        )
        
        # 3. Comparación segura en tiempo constante (evita timing attacks)
        # Convertimos el hash recién generado a hex para comparar contra dk_hex
        dk_check_hex = binascii.hexlify(dk_check).decode()
        
        return hmac.compare_digest(dk_check_hex, dk_hex)
        
    except (ValueError, binascii.Error, TypeError):
        # Si el salt no es hex válido o las iters no son int, falla silenciosamente
        return False