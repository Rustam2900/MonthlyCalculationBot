import logging

from aiogram import Router, types
from aiogram.filters import CommandStart

from bot.header.api import create_user

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def send_welcome(message: types.Message):
    response_message = await create_user(
        telegram_id=message.from_user.id,
        name=message.from_user.first_name,
        username=message.from_user.username
    )
    print("##############")
    print(response_message)
    print("##############")

    await message.answer(text=f"sizdan oldigan malumotlaimiz:\n\n {response_message}", reply_markup=None)
