from decimal import Decimal

from services.balance import calculate_balance


def check_available_funds(user_id, amount):
    if amount <= 0:
        return False, "⚠️ Некоректна сума."

    balance = calculate_balance(user_id)

    available = balance["available"]
    savings = balance["savings"]

    if amount > available:
        return False, (
            "⚠️ Недостатньо доступних коштів!\n\n"
            f"💵 Доступно: "
            f"{Decimal(available) / 100:.2f} грн\n"
            f"🎯 Зарезервовано: "
            f"{Decimal(savings) / 100:.2f} грн\n"
            f"💳 Необхідно: "
            f"{Decimal(amount) / 100:.2f} грн\n\n"
            "Зменш суму або зніми кошти "
            "з накопичень."
        )

    return True, None
