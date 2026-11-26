from decimal import Decimal

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from services.budget import calculate_budget
from keyboards.menus import main_menu

router = Router()


def money(amount):
    return f"{Decimal(amount) / 100:,.2f}".replace(",", " ")


def progress_bar(spent, limit):
    if limit <= 0:
        filled = 10 if spent > 0 else 0
    else:
        filled = min(10, max(0, spent * 10 // limit))

    return "█" * filled + "░" * (10 - filled)


@router.message(F.text == "📅 Місячний бюджет")
async def monthly_budget(message: Message, state: FSMContext):
    await state.clear()

    data = calculate_budget(message.from_user.id)

    text = (
        "📅 Місячний бюджет 65/15/20\n\n"
        f"💵 Доходи: {money(data['income'])} грн\n"
        f"💸 Витрати: {money(data['expense'])} грн\n"
        f"💰 Залишок: {money(data['remaining'])} грн\n\n"
    )

    for group in data["groups"].values():
        limit = group["limit"]
        spent = group["spent"]
        remaining = group["remaining"]

        bar = progress_bar(spent, limit)

        text += (
            f"{group['name']} — {group['percent']}%\n"
            f"{bar}\n"
            f"Ліміт: {money(limit)} грн\n"
            f"Використано: {money(spent)} грн\n"
        )

        if remaining < 0:
            text += (
                f"🔴 Перевищення: "
                f"{money(abs(remaining))} грн\n\n"
            )
        else:
            text += (
                f"🟢 Доступно: "
                f"{money(remaining)} грн\n\n"
            )

    if data["uncategorized"] > 0:
        text += (
            "⚠️ Витрати без категорії: "
            f"{money(data['uncategorized'])} грн\n"
        )

    await message.answer(
        text,
        reply_markup=main_menu
    )
