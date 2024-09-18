import asyncio
import logging

from aiogram import Router, types, Bot
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.markdown import bold

from bot.conustant import START_TEXT
from bot.header.api import create_channels_buttons, save_user_data, check_membership, fetch_channels
from bot.keyboard.keybord import home_buttons

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def send_welcome(message: types.Message):
    user_data = {
        "telegram_id": message.from_user.id,
        "name": message.from_user.full_name,
        "username": message.from_user.username
    }

    status = await save_user_data(user_data)

    if status in (200, 201):
        channels = await fetch_channels()
        tasks = [check_membership(user_data['telegram_id'], channel['channel_id']) for channel in channels]
        results = await asyncio.gather(*tasks)

        if all(results):
            buttons = await home_buttons()
            await message.answer(
                bold("Xizmatlardan birini tanlang"),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=buttons
            )
        else:
            unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
            buttons = await create_channels_buttons(unsubscribed_channels)
            await message.answer(
                bold(START_TEXT),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=buttons
            )
    else:
        await message.answer("Error")
        logger.error(f"Failed to save user data: {user_data}")


@router.callback_query(lambda call: call.data == "check_subscription")
async def check_subscription(call: types.CallbackQuery):
    user_id = call.from_user.id
    channels = await fetch_channels()

    tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
    results = await asyncio.gather(*tasks)

    if all(results):
        # Foydalanuvchi barcha kanallarga obuna bo'lgan
        buttons = await home_buttons()
        await call.message.edit_text(
            "Xizmatlardan birini tanlang",
            reply_markup=buttons
        )
    else:
        unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
        buttons = await create_channels_buttons(unsubscribed_channels)
        await call.message.edit_text(
            bold(START_TEXT),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=buttons
        )


# @router.message(CommandStart())
# async def on_start(message: types.Message, bot: Bot):
#     channel_username = '@Rustam_python_bot'  # Kanalning username ni kiriting
#     channel = await bot.get_chat(channel_username)
#     channel_id = channel.id
#     await message.reply(f"Kanal ID: {channel_id}")

@router.callback_query(lambda c: c.data in ['soatbay'])
async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Salom soatbay")


@router.callback_query(lambda c: c.data in ['home_education'])
async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Salom uyda_talim")


@router.callback_query(lambda c: c.data in ['high_class'])
async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Salom yuqori_sinf")


@router.callback_query(lambda c: c.data in ['primary_class'])
async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Salom boshlangich_sinf")


@router.callback_query(lambda c: c.data in ['decree'])
async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Salom dekret")


@router.callback_query(lambda c: c.data in ['working'])
async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Salom mehnat_tatili")
