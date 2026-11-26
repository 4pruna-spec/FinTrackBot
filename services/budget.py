from database.db import (
    get_monthly_statistics,
    get_monthly_expenses
)

from keyboards.categories import EXPENSE_CATEGORIES


def calculate_budget(user_id):
    income, expense = get_monthly_statistics(user_id)

    needs_limit = income * 65 // 100
    personal_limit = income * 15 // 100
    goals_limit = income - needs_limit - personal_limit

    budget = {
        "needs": {
            "name": "🏠 Основні витрати",
            "percent": 65,
            "limit": needs_limit,
            "spent": 0
        },
        "personal": {
            "name": "🛍️ Особисті витрати",
            "percent": 15,
            "limit": personal_limit,
            "spent": 0
        },
        "goals": {
            "name": "🎯 Фінансові цілі",
            "percent": 20,
            "limit": goals_limit,
            "spent": 0
        }
    }

    uncategorized = 0

    for category, amount in get_monthly_expenses(user_id):
        group = EXPENSE_CATEGORIES.get(category)

        if group in budget:
            budget[group]["spent"] += amount
        else:
            uncategorized += amount

    for group in budget.values():
        group["remaining"] = (
            group["limit"] - group["spent"]
        )

    return {
        "income": income,
        "expense": expense,
        "remaining": income - expense,
        "uncategorized": uncategorized,
        "groups": budget
    }
