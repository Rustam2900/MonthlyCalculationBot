import aiohttp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

BASE_URL = 'http://localhost:8001/api'


async def create_user(telegram_id, name, username):
    url = f"{BASE_URL}/user-create/"

    data = {
        'telegram_id': telegram_id,
        'name': name,
        'username': username,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=data) as response:
            if response.status == 201:
                return "Foydalanuvchi yaratildi."
            else:
                return f"Error: {response.status}"


async def get_mandatory_channels():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/mandatory-users/") as response:
            if response.status == 200:
                return await response.json()
            return []


async def create_channels_buttons():
    channels = await get_mandatory_channels()
    buttons = [
        [InlineKeyboardButton(text=channel['name'], url=channel['url']) for channel in channels],
        [InlineKeyboardButton(text="Azolikni tekshirish ✔️", callback_data="check_subscription")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
