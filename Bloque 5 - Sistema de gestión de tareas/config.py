import os

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-dev-key-change-in-prod")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_SECONDS = 3600          # 1h access token
REFRESH_EXPIRY_SECONDS = 86400 * 7 # 7d refresh token
DATABASE_URL = os.getenv("DATABASE_URL", "task_manager.db")
RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW = 60             # segundos
SERVER_HOST = "127.0.0.1"
SERVER_PORT = int(os.getenv("PORT", 8000))