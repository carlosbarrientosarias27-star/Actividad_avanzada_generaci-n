def detect_cycle(graph, num_nodes):
    # Definición de estados (colores)
    WHITE = 0  # No visitado
    GRAY = 1   # En proceso (en el stack de recursión)
    BLACK = 2  # Procesado completamente

    # Inicializamos todos los nodos como WHITE
    color = [WHITE] * num_nodes

    def has_cycle_dfs(u):
        # Marcamos el nodo actual como GRAY (ancestro activo)
        color[u] = GRAY
        
        # Exploramos todos los vecinos del nodo u
        for v in graph.get(u, []):
            # Si el vecino es GRAY, hemos encontrado una "back-edge" (ciclo)
            if color[v] == GRAY:
                return True
            
            # Si el vecino no ha sido visitado, iniciamos DFS desde él
            if color[v] == WHITE:
                if has_cycle_dfs(v):
                    return True
        
        # Al terminar con sus vecinos, marcamos el nodo como BLACK
        color[u] = BLACK
        return False

    # Iteramos sobre cada nodo para manejar grafos desconectados (bosques)
    for i in range(num_nodes):
        if color[i] == WHITE:
                if has_cycle_dfs(i):
                    return True
                
    return False

# --- Ejemplo de uso ---

# Grafo 1: Con ciclo (0 -> 1 -> 2 -> 0)
graph_with_cycle = {
    0: [1],
    1: [2],
    2: [0],
    3: [4],
    4: []
}

# Grafo 2: Sin ciclo (DAG - Directed Acyclic Graph)
graph_no_cycle = {
    0: [1, 2],
    1: [2],
    2: []
}

print(f"¿Grafo 1 tiene ciclo?: {detect_cycle(graph_with_cycle, 5)}")
print(f"¿Grafo 2 tiene ciclo?: {detect_cycle(graph_no_cycle, 3)}")