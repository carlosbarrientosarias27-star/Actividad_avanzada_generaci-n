import time
from collections import deque
from config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

# Diccionario para almacenar los timestamps de cada IP
_buckets: dict[str, deque] = {}

def is_rate_limited(ip: str) -> bool:
    """
    Comprueba si una IP ha superado el límite de peticiones.
    Implementa un algoritmo de ventana deslizante.
    """
    now = time.time()
    
    # 1. Inicializar el bucket si es la primera vez que vemos la IP
    if ip not in _buckets:
        _buckets[ip] = deque()
    
    bucket = _buckets[ip]
    
    # 2. Limpieza: Eliminar entradas antiguas fuera de la ventana actual
    # Comparamos el timestamp más antiguo con el tiempo actual menos la ventana
    while bucket and bucket[0] < now - RATE_LIMIT_WINDOW:
        bucket.popleft()
    
    # 3. Verificación de límite
    if len(bucket) >= RATE_LIMIT_REQUESTS:
        return True
    
    # 4. Registrar la petición actual y permitir el paso
    bucket.append(now)
    
    # Opcional: Limpieza periódica de memoria para IPs inactivas
    # En una implementación real, se usaría un TTL o una base de datos como Redis.
    
    return False