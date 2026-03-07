from collections import OrderedDict

class LRUCache:
    """
    Caché LRU (Least Recently Used) que garantiza operaciones en tiempo constante.
    
    Atributos:
        capacity (int): Capacidad máxima de la caché.
        cache (OrderedDict): Estructura para mantener el orden de uso y acceso rápido.
    """

    def __init__(self, capacity: int):
        """
        Inicializa la caché.
        
        Complejidad: O(1)
        Raises:
            ValueError: Si la capacidad es menor o igual a 0.
        """
        if capacity <= 0:
            raise ValueError("La capacidad debe ser un entero positivo.")
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        """
        Retorna el valor de la clave si existe, de lo contrario retorna -1.
        Mueve la clave accedida al final para marcarla como 'recientemente usada'.
        
        Complejidad: O(1)
        """
        if key not in self.cache:
            return -1
        
        # Movemos al final para marcar como recientemente usada
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        """
        Inserta o actualiza el valor. Si la caché alcanza su capacidad, 
        desaloja el elemento menos usado (el primero en el OrderedDict).
        
        Complejidad: O(1)
        """
        if key in self.cache:
            # Si ya existe, lo movemos al final tras actualizar
            self.cache.move_to_end(key)
        
        self.cache[key] = value
        
        if len(self.cache) > self.capacity:
            # last=False desaloja el primer elemento (el más antiguo/menos usado)
            self.cache.popitem(last=False)