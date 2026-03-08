from .jwt_handler import decode_token

def _unauthorized(send, message="Unauthorized"):
    """Helper para enviar errores de autenticación."""
    # Enviamos un diccionario, ya que nuestro _send en main.py se encarga del resto
    send(401, {"error": message})

def require_auth(handler):
    """Verifica que la petición incluya un Access Token válido."""
    def wrapper(request, send, *args):
        auth = request.get("headers", {}).get("authorization", "")
        
        if not auth.startswith("Bearer "):
            return _unauthorized(send, "Missing or invalid authorization header")
        
        try:
            # Extraer token y validar que sea de tipo 'access'
            token = auth[7:]
            payload = decode_token(token, expected_type="access")
            
            # Inyectar el payload en la request para uso del handler
            request["user"] = payload
            
        except ValueError as e:
            return _unauthorized(send, str(e))
            
        # Pasar request, send y cualquier argumento extra (como task_id)
        return handler(request, send, *args)
    return wrapper

def require_admin(handler):
    """Verifica que el usuario autenticado tenga rol de administrador."""
    @require_auth
    def wrapper(request, send, *args):
        user = request.get("user", {})
        if user.get("role") != "admin":
            return send(403, {"error": "Forbidden: Admin access required"})
            
        return handler(request, send, *args)
    return wrapper