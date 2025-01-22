from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Получить данные по товару')]
        ],
        resize_keyboard=True
    )
