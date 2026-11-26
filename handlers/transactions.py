from decimal import Decimal, InvalidOperation

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import add_transaction, get_balance

router = Router()


class Transaction(StatesGroup):
    income = State()
    expense = State()


@router.message(F.text == "💰 Мій баланс")
async def balance(message: Message, state: FSMContext):
    await state.clear()
    amount = get_balance(message.from_user.id)

    await message.answer(
        f"💰 Твій баланс: {Decimal(amount) / 100:.2f} грн"
    )


@router.message(F.text == "➕ Додати дохід")
async def income(message: Message, state: FSMContext):
    await state.set_state(Transaction.income)
    await message.answer("💵 Введи суму доходу в гривнях:")


@router.message(F.text == "➖ Додати витрату")
async def expense(message: Message, state: FSMContext):
    await state.set_state(Transaction.expense)
    await message.answer("💸 Введи суму витрати в гривнях:")


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Операцію скасовано.")


@router.message(Transaction.income)
@router.message(Transaction.expense)
async def save_transaction(message: Message, state: FSMContext):
    try:
        amount = Decimal(
            (message.text or "").strip().replace(",", ".")
        )

        if not amount.is_finite():
            raise ValueError

        if amount <= 0 or amount > 1000000000:
            raise ValueError

        if amount * 100 != (amount * 100).to_integral_value():
            raise ValueError

        amount_kopecks = int(amount * 100)

    except (InvalidOperation, ValueError):
        await message.answer(
            "⚠️ Введи коректну суму. Наприклад: 150.50"
        )
        return

    current_state = await state.get_state()

    transaction_type = (
        "income"
        if current_state == Transaction.income.state
        else "expense"
    )

    add_transaction(
        message.from_user.id,
        transaction_type,
        amount_kopecks
    )

    await state.clear()

    balance = get_balance(message.from_user.id)

    await message.answer(
        f"✅ Операцію збережено!\n"
        f"💵 Сума: {amount:.2f} грн\n"
        f"💰 Баланс: {Decimal(balance) / 100:.2f} грн"
    )
