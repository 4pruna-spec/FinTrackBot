from database.db import get_balance
from database.goals import get_total_savings


def calculate_balance(user_id):
    total = get_balance(user_id)
    savings = get_total_savings(user_id)

    available = total - savings

    return {
        "total": total,
        "savings": savings,
        "available": available
    }
