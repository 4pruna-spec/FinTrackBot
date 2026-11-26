from decimal import Decimal

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database.db import get_transactions, get_balance

router = Router()


@router.message(F.text == "📜 Історія операцій")
async def history(message: Message, state: FSMContext):
    await state.clear()

    transactions = get_transactions(message.from_user.id)

    if not transactions:
        await message.answer(
            "📭 У тебе поки немає операцій."
        )
        return

    text = "📜 Останні операції:\n\n"

    for transaction in transactions:
        kind, amount, category, description, date = transaction

        amount = Decimal(amount) / 100

        if kind == "income":
            text += f"🟢 Дохід: +{amount:.2f} грн\n"
        else:
            text += f"🔴 Витрата: -{amount:.2f} грн\n"

        text += f"📅 {date[:10]}\n\n"

    balance = get_balance(message.from_user.id)

    text += f"💰 Баланс: {Decimal(balance) / 100:.2f} грн"

    await message.answer(text)
