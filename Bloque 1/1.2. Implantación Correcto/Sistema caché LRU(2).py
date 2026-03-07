from collections import OrderedDict
import unittest


class LRUCache:
    """
    Implementación de una caché LRU (Least Recently Used).

    La caché mantiene un número máximo de elementos. Cuando se supera la
    capacidad, se elimina el elemento menos recientemente usado.

    Estructura interna:
        collections.OrderedDict

    Complejidad:
        get(key)  -> O(1)
        put(key, value) -> O(1)

    Raises:
        ValueError: si la capacidad es <= 0
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than 0")

        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        """
        Obtiene el valor asociado a la clave.

        Si la clave existe, se marca como recientemente usada moviéndola
        al final del OrderedDict.

        Args:
            key: clave a buscar

        Returns:
            valor asociado o -1 si no existe

        Complejidad:
            O(1)
        """
        if key not in self.cache:
            return -1

        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        """
        Inserta o actualiza un valor en la caché.

        Si la clave ya existe, se actualiza el valor y se marca como
        recientemente usada.

        Si la inserción excede la capacidad, se elimina el elemento
        menos recientemente usado.

        Args:
            key: clave
            value: valor a almacenar

        Complejidad:
            O(1)
        """
        if key in self.cache:
            # Actualizar valor y mover al final
            self.cache.move_to_end(key)

        self.cache[key] = value

        if len(self.cache) > self.capacity:
            # Elimina el menos recientemente usado
            self.cache.popitem(last=False)


# ----------------------
# Unit Tests
# ----------------------

class TestLRUCache(unittest.TestCase):

    def test_capacity_one(self):
        """Edge case: capacidad = 1"""
        cache = LRUCache(1)
        cache.put(1, 10)
        cache.put(2, 20)
        self.assertEqual(cache.get(1), -1)
        self.assertEqual(cache.get(2), 20)

    def test_missing_key(self):
        """Acceso a clave inexistente"""
        cache = LRUCache(2)
        cache.put(1, 1)
        self.assertEqual(cache.get(2), -1)

    def test_overwrite_existing_key(self):
        """Sobrescribir clave existente sin duplicar"""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(1, 100)
        self.assertEqual(cache.get(1), 100)
        self.assertEqual(len(cache.cache), 1)

    def test_correct_eviction(self):
        """El elemento LRU debe ser desalojado"""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        cache.get(1)       # 1 se vuelve MRU
        cache.put(3, 3)    # 2 debe ser desalojado
        self.assertEqual(cache.get(2), -1)
        self.assertEqual(cache.get(1), 1)
        self.assertEqual(cache.get(3), 3)

    def test_alternating_operations(self):
        """Múltiples operaciones alternadas"""
        cache = LRUCache(2)
        cache.put(1, 1)
        cache.put(2, 2)
        self.assertEqual(cache.get(1), 1)
        cache.put(3, 3)      # evict 2
        self.assertEqual(cache.get(2), -1)
        cache.put(4, 4)      # evict 1
        self.assertEqual(cache.get(1), -1)
        self.assertEqual(cache.get(3), 3)
        self.assertEqual(cache.get(4), 4)


if __name__ == "__main__":
    unittest.main()