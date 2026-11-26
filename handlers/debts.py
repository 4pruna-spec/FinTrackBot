from decimal import Decimal, InvalidOperation

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import (
    add_debt,
    get_debts,
    get_debt,
    pay_debt,
    get_debt_payments
)

from keyboards.debts import debts_menu, currency_keyboard
from keyboards.menus import main_menu

router = Router()


class Debt(StatesGroup):
    name = State()
    currency = State()
    amount = State()
    select_debt = State()
    payment = State()
    payment_uah = State()


def money(amount):
    return f"{Decimal(amount) / 100:.2f}"


def parse_amount(text):
    try:
        amount = Decimal(
            (text or "").strip().replace(",", ".")
        )

        if not amount.is_finite():
            return None

        if amount <= 0 or amount > 1000000000:
            return None

        cents = amount * 100

        if cents != cents.to_integral_value():
            return None

        return int(cents)

    except (InvalidOperation, ValueError):
        return None


@router.message(F.text == "💳 Борги")
async def open_debts(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "💳 Управління боргами\n\n"
        "Обери необхідну дію:",
        reply_markup=debts_menu
    )


@router.message(F.text == "🔙 Головне меню")
async def back(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "🏠 Головне меню",
        reply_markup=main_menu
    )


@router.message(Command("cancel"), Debt.name)
@router.message(Command("cancel"), Debt.currency)
@router.message(Command("cancel"), Debt.amount)
@router.message(Command("cancel"), Debt.select_debt)
@router.message(Command("cancel"), Debt.payment)
@router.message(Command("cancel"), Debt.payment_uah)
@router.message(F.text == "❌ Скасувати", Debt.name)
@router.message(F.text == "❌ Скасувати", Debt.currency)
@router.message(F.text == "❌ Скасувати", Debt.amount)
@router.message(F.text == "❌ Скасувати", Debt.select_debt)
@router.message(F.text == "❌ Скасувати", Debt.payment)
@router.message(F.text == "❌ Скасувати", Debt.payment_uah)
async def cancel(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "❌ Операцію скасовано.",
        reply_markup=debts_menu
    )


@router.message(F.text == "➕ Додати борг")
async def new_debt(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Debt.name)

    await message.answer(
        "✏️ Введи назву боргу або ім'я кредитора:"
    )


@router.message(F.text == "📋 Мої борги")
async def list_debts(message: Message, state: FSMContext):
    await state.clear()

    debts = get_debts(message.from_user.id)

    if not debts:
        await message.answer(
            "📭 У тебе поки немає боргів.",
            reply_markup=debts_menu
        )
        return

    totals = {}

    for debt_id, name, currency, total, paid in debts:
        remaining = total - paid
        percent = paid * 100 // total
        filled = min(10, paid * 10 // total)

        bar = "█" * filled + "░" * (10 - filled)

        totals[currency] = (
            totals.get(currency, 0) + remaining
        )

        status = (
            "✅ Погашено"
            if remaining == 0
            else "🔴 Активний"
        )

        await message.answer(
            f"💳 #{debt_id} — {name}\n"
            f"Статус: {status}\n"
            f"Початкова сума: {money(total)} {currency}\n"
            f"Погашено: {money(paid)} {currency}\n"
            f"Залишок: {money(remaining)} {currency}\n"
            f"{bar} {percent}%"
        )

    text = "💰 Загальний залишок боргів:\n\n"

    for currency, amount in totals.items():
        text += f"{currency}: {money(amount)}\n"

    await message.answer(
        text,
        reply_markup=debts_menu
    )


@router.message(F.text == "💵 Погасити борг")
async def start_payment(message: Message, state: FSMContext):
    await state.clear()

    debts = get_debts(message.from_user.id)

    active = [
        debt for debt in debts
        if debt[3] > debt[4]
    ]

    if not active:
        await message.answer(
            "🎉 Активних боргів немає!",
            reply_markup=debts_menu
        )
        return

    for debt_id, name, currency, total, paid in active:
        await message.answer(
            f"#{debt_id} — {name}\n"
            f"Залишок: {money(total - paid)} {currency}"
        )

    await state.set_state(Debt.select_debt)

    await message.answer(
        "Введи номер боргу, який хочеш погасити:"
    )


@router.message(F.text == "📜 Історія погашень")
async def payment_history(
    message: Message,
    state: FSMContext
):
    await state.clear()

    payments = get_debt_payments(message.from_user.id)

    if not payments:
        await message.answer(
            "📭 Платежів поки немає.",
            reply_markup=debts_menu
        )
        return

    text = "📜 Останні погашення:\n\n"

    for name, currency, amount, amount_uah, date in payments:
        text += (
            f"💳 {name}\n"
            f"Сплачено: {money(amount)} {currency}\n"
            f"Витрачено: {money(amount_uah)} грн\n"
            f"📅 {date[:10]}\n\n"
        )

    await message.answer(
        text,
        reply_markup=debts_menu
    )


@router.message(Debt.name)
async def debt_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()

    if not name or len(name) > 100:
        await message.answer(
            "Введи назву від 1 до 100 символів."
        )
        return

    await state.update_data(name=name)
    await state.set_state(Debt.currency)

    await message.answer(
        "💱 Обери валюту боргу:",
        reply_markup=currency_keyboard
    )


@router.message(Debt.currency)
async def debt_currency(message: Message, state: FSMContext):
    if message.text not in ("UAH", "USD", "EUR"):
        await message.answer("Обери валюту кнопкою.")
        return

    await state.update_data(currency=message.text)
    await state.set_state(Debt.amount)

    await message.answer("💵 Введи суму боргу:")


@router.message(Debt.amount)
async def debt_amount(message: Message, state: FSMContext):
    amount = parse_amount(message.text)

    if amount is None:
        await message.answer("⚠️ Введи коректну суму.")
        return

    data = await state.get_data()

    add_debt(
        message.from_user.id,
        data["name"],
        data["currency"],
        amount
    )

    await state.clear()

    await message.answer(
        "✅ Борг успішно додано!\n\n"
        f"Назва: {data['name']}\n"
        f"Сума: {money(amount)} {data['currency']}",
        reply_markup=debts_menu
    )


@router.message(Debt.select_debt)
async def select_debt(message: Message, state: FSMContext):
    try:
        debt_id = int(message.text or "")
    except ValueError:
        await message.answer("Введи номер боргу цифрами.")
        return

    debt = get_debt(message.from_user.id, debt_id)

    if not debt or debt[3] <= debt[4]:
        await message.answer("⚠️ Активний борг не знайдено.")
        return

    await state.update_data(
        debt_id=debt_id,
        currency=debt[2],
        remaining=debt[3] - debt[4]
    )

    await state.set_state(Debt.payment)

    await message.answer(
        f"💵 Введи суму погашення в {debt[2]}:"
    )


@router.message(Debt.payment)
async def payment(message: Message, state: FSMContext):
    amount = parse_amount(message.text)
    data = await state.get_data()

    if amount is None or amount > data["remaining"]:
        await message.answer(
            "⚠️ Некоректна сума або перевищено залишок."
        )
        return

    await state.update_data(payment=amount)

    if data["currency"] == "UAH":
        await finish_payment(message, state, amount)
    else:
        await state.set_state(Debt.payment_uah)

        await message.answer(
            "Введи фактично витрачену суму в гривнях:"
        )


@router.message(Debt.payment_uah)
async def payment_uah(message: Message, state: FSMContext):
    amount = parse_amount(message.text)

    if amount is None:
        await message.answer("⚠️ Введи коректну суму.")
        return

    await finish_payment(message, state, amount)


async def finish_payment(message, state, amount_uah):
    data = await state.get_data()

    success = pay_debt(
        message.from_user.id,
        data["debt_id"],
        data["payment"],
        amount_uah
    )

    await state.clear()

    if not success:
        await message.answer(
            "⚠️ Не вдалося погасити борг.",
            reply_markup=debts_menu
        )
        return

    debt = get_debt(
        message.from_user.id,
        data["debt_id"]
    )

    remaining = debt[3] - debt[4]

    text = (
        "✅ Платіж збережено!\n\n"
        f"💵 Сплачено: {money(data['payment'])} "
        f"{data['currency']}\n"
        f"💳 Залишок: {money(remaining)} "
        f"{data['currency']}\n\n"
        "📊 Платіж враховано в бюджеті 65/15/20."
    )

    if remaining == 0:
        text += "\n\n🎉 Борг повністю погашено!"

    await message.answer(
        text,
        reply_markup=debts_menu
    )
