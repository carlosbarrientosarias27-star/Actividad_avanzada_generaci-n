import threading
import time
import unittest
from unittest.mock import patch

class RateLimiter:
    def __init__(self, max_requests: int = 100, window: int = 60):
        self.max_requests = max_requests
        # Tasa de regeneración: tokens por segundo
        self.refill_rate = max_requests / window  
        self.expiry_duration = 60
        
        # Diccionario para almacenar el estado de cada IP
        # {ip: {"tokens": float, "last_refill": float, "last_access": float}}
        self.buckets = {}
        self.lock = threading.Lock()

    def _refill(self, ip: str, current_time: float):
        """Calcula y añade tokens basados en el tiempo transcurrido (O(1))."""
        bucket = self.buckets[ip]
        elapsed = current_time - bucket["last_refill"]
        
        # Algoritmo Token Bucket Puro
        new_tokens = elapsed * self.refill_rate
        bucket["tokens"] = min(self.max_requests, bucket["tokens"] + new_tokens)
        bucket["last_refill"] = current_time

    def _cleanup(self, current_time: float):
        """Elimina IPs inactivas por más de 60s para liberar memoria (O(1) amortizado)."""
        # Nota: En Python, iterar y borrar requiere una lista intermedia de llaves
        expired_ips = [
            ip for ip, data in self.buckets.items() 
            if current_time - data["last_access"] > self.expiry_duration
        ]
        for ip in expired_ips:
            del self.buckets[ip]

    def is_allowed(self, ip: str) -> bool:
        """Determina si una IP tiene tokens disponibles para la petición."""
        now = time.time()
        
        with self.lock:
            # 1. Limpieza de IPs obsoletas
            self._cleanup(now)
            
            # 2. Inicialización si la IP es nueva
            if ip not in self.buckets:
                self.buckets[ip] = {
                    "tokens": float(self.max_requests),
                    "last_refill": now,
                    "last_access": now
                }
            
            # 3. Recarga perezosa de tokens
            self._refill(ip, now)
            self.buckets[ip]["last_access"] = now
            
            # 4. Consumo de token
            if self.buckets[ip]["tokens"] >= 1:
                self.buckets[ip]["tokens"] -= 1
                return True
            return False

# --- SECCIÓN DE PRUEBAS UNITARIAS ---

class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        # Configuración: 100 tokens cada 60 segundos
        self.limiter = RateLimiter(max_requests=100, window=60)

    @patch('time.time')
    def test_ip_nueva_permitida(self, mock_time):
        """Caso (a): IP nueva debe ser permitida con saldo lleno."""
        mock_time.return_value = 1000.0
        self.assertTrue(self.limiter.is_allowed("1.1.1.1"))

    @patch('time.time')
    def test_supera_limite(self, mock_time):
        """Caso (b): IP que consume todos sus tokens debe ser bloqueada."""
        mock_time.return_value = 1000.0
        for _ in range(100):
            self.limiter.is_allowed("1.1.1.1")
        self.assertFalse(self.limiter.is_allowed("1.1.1.1"))

    @patch('time.time')
    def test_ip_expirada_se_resetea(self, mock_time):
        """Caso (c): IP sin actividad > 60s se elimina del sistema."""
        mock_time.return_value = 1000.0
        self.limiter.is_allowed("1.1.1.1")
        
        # Avanzar 61 segundos
        mock_time.return_value = 1061.0
        # Forzar un ciclo de cleanup con otra IP
        self.limiter.is_allowed("2.2.2.2")
        
        self.assertNotIn("1.1.1.1", self.limiter.buckets)

    @patch('time.time')
    def test_recarga_tras_espera(self, mock_time):
        """Caso (e): Los tokens se recuperan proporcionalmente al tiempo."""
        mock_time.return_value = 1000.0
        # Agotar tokens
        for _ in range(100): self.limiter.is_allowed("1.1.1.1")
        self.assertFalse(self.limiter.is_allowed("1.1.1.1"))
        
        # Esperar 6 segundos (debería recargar 10 tokens: 100/60 * 6)
        mock_time.return_value = 1006.0
        self.assertTrue(self.limiter.is_allowed("1.1.1.1"))
        # Verificar que podemos consumir los que se recargaron
        for _ in range(9): 
            self.assertTrue(self.limiter.is_allowed("1.1.1.1"))

    @patch('time.time')
    def test_multiples_ips_independientes(self, mock_time):
        """Caso (f): El límite de una IP no afecta a las demás."""
        mock_time.return_value = 1000.0
        # Agotar IP A
        for _ in range(100): self.limiter.is_allowed("A")
        
        self.assertFalse(self.limiter.is_allowed("A"))
        self.assertTrue(self.limiter.is_allowed("B"), "IP B debería tener sus propios tokens")

    @patch('time.time')
    def test_concurrencia_threads(self, mock_time):
        """Caso (d): Verificación de thread-safety bajo estrés."""
        mock_time.return_value = 1000.0
        limiter = RateLimiter(max_requests=50, window=60)
        
        def worker():
            for _ in range(10):
                limiter.is_allowed("thread-ip")

        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads: t.start()
        for t in threads: t.join()

        # Se consumieron exactamente 50 tokens entre 5 hilos
        self.assertFalse(limiter.is_allowed("thread-ip"), "El bucket debería estar vacío")

if __name__ == "__main__":
    # Ejecutar los tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)