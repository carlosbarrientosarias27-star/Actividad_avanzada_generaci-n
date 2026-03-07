⚠️
Código generado por IA — busca los errores:

class LRUCache:
def __init__(self, capacity: int):
self.capacity = capacity
self.cache = {}
self.order = []
def get(self, key: int) -> int:
if key in self.cache:
self.order.remove(key) # ← O(n) en lista
self.order.append(key)
return self.cache[key]
return -1
def put(self, key: int, value: int) -> None:
if key in self.cache:
self.order.remove(key)
elif len(self.cache) >= self.capacity:
oldest = self.order.pop(0) # ← O(n) en lista
del self.cache[oldest]
self.cache[key] = value
self.order.append(key)