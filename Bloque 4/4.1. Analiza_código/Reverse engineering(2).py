from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
from collections import defaultdict

@dataclass
class Transaction:
    """Representa una transacción financiera individual."""
    id: str
    amount: float
    currency: str
    timestamp: datetime
    category: str
    description: Optional[str] = None

def analyze_spending(
    transactions: List[Transaction], 
    month: int, 
    year: int, 
    currency: str = "EUR"
) -> Dict[str, float]:
    """
    Procesa una lista de transacciones y devuelve un resumen de gastos por categoría
    para un mes, año y moneda específicos.

    Args:
        transactions (List[Transaction]): Lista de objetos Transaction a analizar.
        month (int): El mes del año (1-12).
        year (int): El año de las transacciones.
        currency (str): El código de moneda para filtrar (por defecto "EUR").

    Returns:
        Dict[str, float]: Un diccionario donde las llaves son las categorías 
                          y los valores son la suma de los montos.

    Raises:
        ValueError: Si la lista de transacciones está vacía.
    """
    if not transactions:
        raise ValueError("La lista de transacciones no puede estar vacía.")

    # Diccionario para acumular los gastos por categoría
    summary: Dict[str, float] = defaultdict(float)

    for tx in transactions:
        # Filtramos por mes, año y moneda
        if (tx.timestamp.month == month and 
            tx.timestamp.year == year and 
            tx.currency == currency):
            
            summary[tx.category] += tx.amount

    return dict(summary)