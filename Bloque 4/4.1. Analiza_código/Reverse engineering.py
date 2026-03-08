from typing import Optional, List 
from dataclasses import dataclass 
from datetime import datetime

@dataclass
class Transaction: 
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
    currency: str = 'EUR'
) -> dict:
    """
    Analiza gastos mensuales agrupados por categoría. Filtra por mes/año y convierte a moneda base.
    Raises ValueError si transactions está vacío. """
    if not transactions:
        raise ValueError('Lista de transacciones vacía')
    ...
