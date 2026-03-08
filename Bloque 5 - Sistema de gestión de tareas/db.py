import sqlite3
from config import DATABASE_URL

def get_conn() -> sqlite3.Connection:
    """Crea y configura una conexión a la base de datos."""
    conn = sqlite3.connect(DATABASE_URL)
    # Permite acceder a las columnas por nombre: fila['username']
    conn.row_factory = sqlite3.Row 
    # Mejora el rendimiento en escrituras/lecturas concurrentes
    conn.execute("PRAGMA journal_mode=WAL")
    # Asegura que las restricciones de FOREIGN KEY se respeten
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    """Inicializa el esquema de la base de datos."""
    conn = get_conn()
    try:
        with conn:
            # 1. Creación de Tablas
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT UNIQUE NOT NULL,
                email         TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role          TEXT NOT NULL DEFAULT 'user',
                created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                description TEXT,
                status      TEXT NOT NULL DEFAULT 'pending',
                owner_id    INTEGER NOT NULL,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS refresh_tokens (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                token      TEXT UNIQUE NOT NULL,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER,
                method     TEXT,
                path       TEXT,
                status     INTEGER,
                ip         TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            -- 2. Índices para optimizar búsquedas
            CREATE INDEX IF NOT EXISTS idx_tasks_owner ON tasks(owner_id);
            CREATE INDEX IF NOT EXISTS idx_tokens_user ON refresh_tokens(user_id);

            -- 3. Trigger para actualizar la fecha de 'updated_at' automáticamente
            CREATE TRIGGER IF NOT EXISTS update_task_timestamp 
            AFTER UPDATE ON tasks
            FOR EACH ROW
            BEGIN
                UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = old.id;
            END;
            """)
    finally:
        conn.close()