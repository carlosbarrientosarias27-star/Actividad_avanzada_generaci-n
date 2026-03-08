from db import get_conn

def log(user_id, method: str, path: str, status: int, ip: str):
    """
    Registra una actividad en la tabla audit_logs.
    Garantiza que un fallo en el log no interrumpa el flujo del servidor.
    """
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO audit_logs (user_id, method, path, status, ip) VALUES (?, ?, ?, ?, ?)",
                (user_id, method, path, status, ip)
            )
            # Confirmar los cambios para que se guarden físicamente
            conn.commit()
    except Exception as e:
        # Opcional: imprimir el error en consola para depuración, 
        # pero sin lanzar la excepción hacia arriba.
        print(f"Error en Audit Log: {e}") 
        pass