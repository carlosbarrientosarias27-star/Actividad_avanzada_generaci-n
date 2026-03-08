from datetime import datetime
from collections import defaultdict

EXCHANGE_RATES = {
    "USD": 1.0,
    "EUR": 1.09,   # 1 EUR = 1.09 USD
    "GBP": 1.27,
    "JPY": 0.0067,
    "MXN": 0.058,
    "BRL": 0.20,
    "CAD": 0.74,
    "ARS": 0.0011,
}

BASE_CURRENCY = "USD"


def analyze_spending(
    transactions: list[dict],
    month: int,
    year: int,
    base_currency: str = BASE_CURRENCY,
) -> dict:
    """
    Analyze spending for a given month/year.

    Each transaction is expected to have:
      - timestamp: datetime | str (ISO 8601)
      - amount: float
      - currency: str  (e.g. "EUR", "USD")
      - category: str

    Returns:
      {
        "categories": {category: total, ...},
        "total_spend": float,
        "transaction_count": int,
        "months_without_data": bool,
      }
    """

    def _to_base(amount: float, currency: str) -> float:
        """Convert amount to base currency via hardcoded rates."""
        rate_from = EXCHANGE_RATES.get(currency.upper(), 1.0)
        rate_to = EXCHANGE_RATES.get(base_currency.upper(), 1.0)
        return amount * (rate_from / rate_to)

    def _parse_ts(ts) -> datetime:
        if isinstance(ts, datetime):
            return ts
        return datetime.fromisoformat(str(ts))

    # (1) Filter by month and year
    filtered = [
        t for t in transactions
        if _parse_ts(t["timestamp"]).month == month
        and _parse_ts(t["timestamp"]).year == year
    ]

    # (5) No transactions → return empty structure without raising
    if not filtered:
        return {
            "categories": {},
            "total_spend": 0.0,
            "transaction_count": 0,
            "months_without_data": True,
        }

    # (2 & 3) Convert to base currency and group by category
    category_totals: dict[str, float] = defaultdict(float)

    for t in filtered:
        converted = _to_base(t["amount"], t.get("currency", base_currency))
        category_totals[t["category"]] += converted

    # (3) Round each category total to 2 decimals
    categories = {cat: round(total, 2) for cat, total in category_totals.items()}

    # (4) Build and return result dict
    total_spend = round(sum(categories.values()), 2)

    return {
        "categories": categories,
        "total_spend": total_spend,
        "transaction_count": len(filtered),
        "months_without_data": False,
    }