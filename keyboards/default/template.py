from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

shablon = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Test"),
            KeyboardButton(text="Test"),
        ],
    ],
    resize_keyboard=True 
)
