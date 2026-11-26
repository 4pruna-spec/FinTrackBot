from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Мій баланс")],
        [
            KeyboardButton(text="➕ Додати дохід"),
            KeyboardButton(text="➖ Додати витрату")
        ],
        [
            KeyboardButton(text="📊 Статистика"),
            KeyboardButton(text="📜 Історія операцій")
        ],
        [
            KeyboardButton(text="💳 Борги"),
            KeyboardButton(text="🎯 Накопичення")
        ],
        [KeyboardButton(text="📅 Місячний бюджет")],
        [KeyboardButton(text="⚙️ Налаштування")]
    ],
    resize_keyboard=True
)
