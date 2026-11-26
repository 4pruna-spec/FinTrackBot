from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


debts_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📋 Мої борги")
        ],
        [
            KeyboardButton(text="➕ Додати борг"),
            KeyboardButton(text="💵 Погасити борг")
        ],
        [
            KeyboardButton(text="📜 Історія погашень")
        ],
        [
            KeyboardButton(text="🔙 Головне меню")
        ]
    ],
    resize_keyboard=True
)


currency_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="UAH"),
            KeyboardButton(text="USD"),
            KeyboardButton(text="EUR")
        ],
        [
            KeyboardButton(text="❌ Скасувати")
        ]
    ],
    resize_keyboard=True
)
