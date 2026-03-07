from typing import Dict, List

def has_cycle(graph: Dict[int, List[int]]) -> bool:
    # 0: Blanco (No visitado), 1: Gris (Visitando/En Stack), 2: Negro (Procesado)
    state = {node: 0 for node in graph}
    
    # Iteramos por cada nodo para manejar grafos desconectados y nodos aislados (Requisito 2 y 3)
    for node in graph:
        if state[node] == 0:
            # Stack guarda: [nodo, índice_del_próximo_vecino_a_explorar]
            # Usamos stack explícito para evitar RecursionError (Requisito 4 y 5)
            stack = [[node, 0]]
            
            while stack:
                current_node, neighbor_idx = stack[-1]
                
                if neighbor_idx == 0:
                    # Marcamos como "Gris" al entrar por primera vez
                    state[current_node] = 1
                
                # ¿Ya revisamos todos los vecinos de este nodo?
                neighbors = graph.get(current_node, [])
                if neighbor_idx < len(neighbors):
                    neighbor = neighbors[neighbor_idx]
                    
                    # Actualizamos el índice en el stack para la próxima vuelta
                    stack[-1][1] += 1
                    
                    if state.get(neighbor, 0) == 1:
                        # Si el vecino es "Gris", hay un ciclo (Back-edge)
                        return True
                    
                    if state.get(neighbor, 0) == 0:
                        # Si es "Blanco", bajamos en profundidad
                        stack.append([neighbor, 0])
                else:
                    # Terminamos con el nodo: lo marcamos como "Negro" y sacamos del stack
                    state[current_node] = 2
                    stack.pop()
                    
    return False

# --- Ejemplo de prueba con 10,000 nodos (Requisito 4) ---
# Un grafo lineal gigante: 0 -> 1 -> 2 -> ... -> 9999
huge_graph = {i: [i + 1] for i in range(9999)}
huge_graph[9999] = [] # Nodo final sin salida
print(f"¿Tiene ciclo el grafo gigante?: {has_cycle(huge_graph)}") 

# Añadiendo un ciclo al final: 9999 -> 0
huge_graph[9999] = [0]
print(f"¿Tiene ciclo ahora?: {has_cycle(huge_graph)}")