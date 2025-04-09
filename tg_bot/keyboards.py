from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    kb = [
        [KeyboardButton(text="⬇️ Загрузить статью")],
        [KeyboardButton(text="📊 Суммаризация")],
        [KeyboardButton(text="❓ Задать вопрос")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)