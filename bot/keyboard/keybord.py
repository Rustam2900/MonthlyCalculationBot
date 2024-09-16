from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu():
    kb = [
        [KeyboardButton(text=ORDERS), KeyboardButton(text=MY_ORDERS)],
        [KeyboardButton(text=OPERATOR), KeyboardButton(text=SETTINGS)],
        [KeyboardButton(text=WEB_ORDERS)]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    return keyboard
