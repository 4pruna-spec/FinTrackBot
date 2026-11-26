from decimal import Decimal

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from services.budget import calculate_budget
from services.balance import calculate_balance
from keyboards.menus import main_menu

router = Router()


def money(amount):
    return f"{Decimal(amount) / 100:.2f} грн"


def progress_bar(spent, limit):
    if limit <= 0:
        return "░" * 10

    filled = max(0, min(10, spent * 10 // limit))

    return "█" * filled + "░" * (10 - filled)


@router.message(F.text == "📅 Місячний бюджет")
async def monthly_budget(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.from_user.id

    budget = calculate_budget(user_id)
    balance = calculate_balance(user_id)

    text = (
        "📅 Місячний бюджет 65/15/20\n\n"
        f"➕ Доходи: {money(budget['income'])}\n"
        f"➖ Витрати: {money(budget['expense'])}\n"
        f"🎯 Накопичення за місяць: "
        f"{money(budget['savings'])}\n"
        f"💵 Залишок бюджету: "
        f"{money(budget['remaining'])}\n\n"
        "━━━━━━━━━━━━━━\n\n"
    )

    for group in budget["groups"].values():

        limit = group["limit"]
        spent = group["spent"]
        remaining = group["remaining"]

        percent = (
            spent * 100 // limit
            if limit > 0
            else 0
        )

        text += (
            f"{group['name']} — {group['percent']}%\n"
            f"{progress_bar(spent, limit)} {percent}%\n"
            f"Ліміт: {money(limit)}\n"
            f"Використано: {money(spent)}\n"
        )

        if remaining >= 0:
            text += (
                f"🟢 Доступно: {money(remaining)}\n\n"
            )
        else:
            text += (
                f"🔴 Перевитрата: "
                f"{money(abs(remaining))}\n\n"
            )

    if budget["uncategorized"] > 0:
        text += (
            "⚠️ Витрати без категорії: "
            f"{money(budget['uncategorized'])}\n\n"
        )

    text += (
        "━━━━━━━━━━━━━━\n\n"
        f"💰 Доступний баланс: "
        f"{money(balance['available'])}\n"
        f"🎯 Загалом накопичено: "
        f"{money(balance['savings'])}\n"
        f"🏦 Загальна сума коштів: "
        f"{money(balance['total'])}"
    )

    await message.answer(
        text,
        reply_markup=main_menu
    )
