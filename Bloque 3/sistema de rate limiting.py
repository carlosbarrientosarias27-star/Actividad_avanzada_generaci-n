import threading
import time
import unittest
from unittest.mock import patch

class RateLimiter:
    def __init__(self, max_requests: int = 100, window: int = 60):
        self.max_requests = max_requests
        self.refill_rate = max_requests / window  
        self.expiry_duration = 60
        self.buckets = {}
        self.lock = threading.Lock()
        
        # Hilo de fondo para producción
        self.cleanup_thread = threading.Thread(target=self._run_periodic_cleanup, daemon=True)
        self.cleanup_thread.start()

    def _run_periodic_cleanup(self):
        """Loop infinito para el hilo de fondo."""
        while True:
            time.sleep(self.expiry_duration)
            self.run_cleanup(time.time())

    def run_cleanup(self, current_time: float):
        """Lógica de limpieza expuesta para ser testeable (O(n) controlado)."""
        with self.lock:
            expired_ips = [
                ip for ip, data in self.buckets.items() 
                if current_time - data["last_access"] > self.expiry_duration
            ]
            for ip in expired_ips:
                del self.buckets[ip]

    def is_allowed(self, ip: str) -> bool:
        now = time.time()
        with self.lock:
            # OPTIMIZACIÓN: Ya no llamamos a la limpieza aquí.
            # Esto hace que la validación sea O(1).
            if ip not in self.buckets:
                self.buckets[ip] = {
                    "tokens": float(self.max_requests),
                    "last_refill": now,
                    "last_access": now
                }
            
            self._refill(ip, now)
            self.buckets[ip]["last_access"] = now
            
            if self.buckets[ip]["tokens"] >= 1:
                self.buckets[ip]["tokens"] -= 1
                return True
            return False

    def _refill(self, ip: str, current_time: float):
        bucket = self.buckets[ip]
        elapsed = current_time - bucket["last_refill"]
        new_tokens = elapsed * self.refill_rate
        bucket["tokens"] = min(self.max_requests, bucket["tokens"] + new_tokens)
        bucket["last_refill"] = current_time

    def is_allowed(self, ip: str) -> bool:
        """
        Determina si una IP tiene tokens disponibles (O(1)).
        
        Args:
            ip (str): La dirección IP del cliente.
        Returns:
            bool: True si la petición es permitida, False en caso contrario.
        """
        now = time.time()
        # ... resto del código con su indentación correcta ...
        with self.lock:
            # OPTIMIZACIÓN: Ya no llamamos a _cleanup aquí. Complejidad O(1).
            if ip not in self.buckets:
                self.buckets[ip] = {
                    "tokens": float(self.max_requests),
                    "last_refill": now,
                    "last_access": now
                }
            
            self._refill(ip, now)
            self.buckets[ip]["last_access"] = now
            
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
        """Caso (c): Ahora invocamos run_cleanup con el tiempo simulado."""
        mock_time.return_value = 1000.0
        self.limiter.is_allowed("1.1.1.1")
        
        # Avanzar 61 segundos en el simulador
        mock_time.return_value = 1061.0
        
        # Forzamos la limpieza usando el tiempo del mock
        self.limiter.run_cleanup(1061.0)
        
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