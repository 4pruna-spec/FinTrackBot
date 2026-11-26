from decimal import Decimal

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database.db import get_monthly_statistics

router = Router()


@router.message(F.text == "📊 Статистика")
async def statistics(message: Message, state: FSMContext):
    await state.clear()

    income, expense = get_monthly_statistics(
        message.from_user.id
    )

    income = Decimal(income) / 100
    expense = Decimal(expense) / 100

    balance = income - expense

    savings_percent = (
        balance / income * 100 if income > 0 else 0
    )

    await message.answer(
        "📊 Статистика за поточний місяць\n\n"
        f"🟢 Доходи: {income:.2f} грн\n"
        f"🔴 Витрати: {expense:.2f} грн\n\n"
        f"💰 Залишок: {balance:.2f} грн\n"
        f"📈 Частка заощаджень: {savings_percent:.1f}%"
    )
