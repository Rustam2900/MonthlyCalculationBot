from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from bot.conustant import SOATBAY_TEXT, HOMEEDUCATION_TEXT, HIGHCLASS_TEXT, PRIMARYCLASS_TEXT, DECREE_TEXT, WORKING_TEXT


async def home_buttons():
    buttons = [
        [InlineKeyboardButton(text=SOATBAY_TEXT, callback_data='soatbay')],
        [InlineKeyboardButton(text=HOMEEDUCATION_TEXT, callback_data='home_education')],
        [InlineKeyboardButton(text=HIGHCLASS_TEXT, callback_data='high_class')],
        [InlineKeyboardButton(text=PRIMARYCLASS_TEXT, callback_data='primary_class')],
        [InlineKeyboardButton(text=DECREE_TEXT, callback_data='decree')],
        [InlineKeyboardButton(text=WORKING_TEXT, callback_data='working')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# async def home_buttons():
#     buttons = [
#         [KeyboardButton(text=SOATBAY_TEXT)],
#         [KeyboardButton(text=HOMEEDUCATION_TEXT)],
#         [KeyboardButton(text=HIGHCLASS_TEXT)],
#         [KeyboardButton(text=PRIMARYCLASS_TEXT)],
#         [KeyboardButton(text=DECREE_TEXT)],
#         [KeyboardButton(text=WORKING_TEXT)],
#     ]
#     return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
