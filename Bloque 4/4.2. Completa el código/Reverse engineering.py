from datetime import datetime

def analyze_spending(transactions, month, year):
    # 1. Configuración inicial
    EXCHANGE_RATES = {
        "USD": 0.92,  # 1 USD = 0.92 EUR
        "EUR": 1.0,   # Base
        "GBP": 1.17   # 1 GBP = 1.17 EUR
    }
    
    # Estructura por defecto para cuando no hay datos
    empty_result = {
        "category": {},
        "total_spend": 0.0,
        "transaction_count": 0,
        "months_without_data": True
    }

    category_totals = {}
    grand_total = 0.0
    count = 0

    # 2. Filtrado y Procesamiento
    for tx in transactions:
        # Asumiendo que tx['timestamp'] es un objeto datetime o un string ISO
        ts = tx['timestamp']
        if isinstance(ts, str):
            ts = datetime.fromisoformat(ts)

        # (1) Filtrar por mes y año
        if ts.month == month and ts.year == year:
            # (2) Conversión de moneda
            amount = tx['amount']
            currency = tx.get('currency', 'EUR')
            rate = EXCHANGE_RATES.get(currency, 1.0)
            
            amount_in_base = amount * rate
            
            # (3) Agrupar por categoría
            cat = tx['category']
            category_totals[cat] = category_totals.get(cat, 0.0) + amount_in_base
            
            grand_total += amount_in_base
            count += 1

    # (5) Si no hay transacciones, devolver estructura vacía
    if count == 0:
        return empty_result

    # (4) Devolver dict con valores redondeados
    return {
        "category": {k: round(v, 2) for k, v in category_totals.items()},
        "total_spend": round(grand_total, 2),
        "transaction_count": count,
        "months_without_data": False
    }