import logging

from aiogram import Router, types
from aiogram.client.session import aiohttp
from aiogram.filters import CommandStart

from bot.conustant import START_TEXT
from bot.header.api import create_user, create_channels_buttons, check_user_registration

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def send_welcome(message: types.Message):
    telegram_id = message.from_user.id
    async with aiohttp.ClientSession() as session:
        is_user_registered = await check_user_registration(session, telegram_id)
    if not is_user_registered:
        response_message = await create_user(
            telegram_id=message.from_user.id,
            name=message.from_user.first_name,
            username=message.from_user.username
        )
        await message.answer(text=START_TEXT,
                             reply_markup=await create_channels_buttons())
    else:
        await message.answer(text='salom')
