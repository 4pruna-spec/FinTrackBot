from decimal import Decimal

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database.db import get_monthly_statistics
from database.goals import (
    get_monthly_savings,
    get_total_savings
)

from services.balance import calculate_balance
from keyboards.menus import main_menu

router = Router()


def money(amount):
    return f"{Decimal(amount) / 100:.2f} грн"


@router.message(F.text == "📊 Статистика")
async def statistics(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.from_user.id

    income, expense = get_monthly_statistics(user_id)

    savings = get_monthly_savings(user_id)
    total_savings = get_total_savings(user_id)

    balance = calculate_balance(user_id)

    net = income - expense
    free_cash = net - savings

    savings_percent = (
        savings / income * 100
        if income > 0
        else 0
    )

    await message.answer(
        "📊 Статистика за поточний місяць\n\n"
        f"➕ Доходи: {money(income)}\n"
        f"➖ Витрати: {money(expense)}\n"
        f"🎯 Чисті накопичення: {money(savings)}\n\n"
        f"📈 Чистий грошовий потік: {money(net)}\n"
        f"💵 Залишок після накопичень: "
        f"{money(free_cash)}\n\n"
        f"📊 Частка накопичень: "
        f"{savings_percent:.1f}%\n\n"
        "━━━━━━━━━━━━━━\n\n"
        f"🏦 Загалом накопичено: "
        f"{money(total_savings)}\n"
        f"💰 Доступний баланс: "
        f"{money(balance['available'])}",
        reply_markup=main_menu
    )
