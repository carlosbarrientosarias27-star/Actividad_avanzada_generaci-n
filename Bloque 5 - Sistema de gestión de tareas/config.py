import os
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# --- SEGURIDAD ---
# En producción, NUNCA uses la clave por defecto.
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-dev-key-change-in-prod")
JWT_ALGORITHM = "HS256"

# Validar que se cambie la clave en entornos reales
if os.getenv("ENV") == "production" and SECRET_KEY == "super-secret-dev-key-change-in-prod":
    raise ValueError("¡ERROR CRÍTICO: Debes configurar una SECRET_KEY segura en producción!")

# --- TIEMPOS DE EXPIRACIÓN (en segundos) ---
JWT_EXPIRY_SECONDS = int(os.getenv("JWT_EXPIRY", 3600))          # 1 hora
REFRESH_EXPIRY_SECONDS = int(os.getenv("REFRESH_EXPIRY", 604800)) # 7 días

# --- BASE DE DATOS ---
# Aseguramos que la ruta sea absoluta para evitar errores de "file not found"
DATABASE_NAME = os.getenv("DATABASE_URL", "task_manager.db")
DATABASE_URL = str(BASE_DIR / DATABASE_NAME)

# --- RATE LIMITING ---
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", 60))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))     # 1 minuto

# --- SERVIDOR ---
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("PORT", 8000))