from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.conustant import *


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


async def category_buttons():
    buttons = [
        [InlineKeyboardButton(text=HIGH_CATEGORY_TEXT, callback_data='high_category')],
        [
            InlineKeyboardButton(text=CATEGORY_1_TEXT, callback_data='category_1'),
            InlineKeyboardButton(text=CATEGORY_2_TEXT, callback_data='category_2')
        ],
        [
            InlineKeyboardButton(text=SPECIALIST_TEXT, callback_data='specialist'),
            InlineKeyboardButton(text=MIDDLE_SPECIALIST_TEXT, callback_data='middle_specialist')
        ],
        [InlineKeyboardButton(text=BACK_TEXT, callback_data='back')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def confirmation_buttons():
    buttons = [
        [
            InlineKeyboardButton(text=YES_TEXT, callback_data='yes'),
            InlineKeyboardButton(text=NO_TEXT, callback_data='no')
        ],
        [InlineKeyboardButton(text=BACK_TEXT, callback_data='back')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def beck_buttons():
    buttons = [

        [InlineKeyboardButton(text=BACK_TEXT, callback_data='back')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def beck_days_buttons():
    buttons = [
        [InlineKeyboardButton(text="24 kun", callback_data='24days'),
         InlineKeyboardButton(text="36 kun", callback_data='36days')
         ],
        [InlineKeyboardButton(text="48 kun", callback_data='48days')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
