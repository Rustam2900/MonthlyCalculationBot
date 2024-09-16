import asyncio
import logging

import aiohttp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot
from bot.config import BOT_TOKEN

BASE_URL = 'http://localhost:8001/api'
logger = logging.getLogger(__name__)

bot = Bot(BOT_TOKEN)


async def save_user_data(user_data):
    user_data = {k: v for k, v in user_data.items() if v is not None}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/user/{user_data['telegram_id']}") as response:
            if response.status == 200:
                async with session.put(f"{BASE_URL}/user-update/{user_data['telegram_id']}/",
                                       json=user_data) as update_response:
                    if update_response.status not in (200, 204):
                        logger.error(
                            f"update user: {update_response.status} - {await update_response.text()}")
            elif response.status == 404:
                async with session.post(f"{BASE_URL}/user-create/", json=user_data) as create_response:
                    if create_response.status not in (200, 201):
                        logger.error(
                            f"create user: {create_response.status} - {await create_response.text()}")
            else:
                logger.error(f"check user data: {response.status} - {await response.text()}")
    return response.status


async def save_multiple_users(user_data_list):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for user_data in user_data_list:
            task = save_user_data(user_data)
            tasks.append(task)
        results = await asyncio.gather(*tasks)
        return results


async def check_user_registration(session, telegram_id):
    url = f"{BASE_URL}/user/{telegram_id}"
    async with session.get(url) as response:
        print(f"User registration check URL: {url}")
        print(f"User registration check response status: {response.status}")
        return response.status == 200


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


async def check_subscription(user_id):
    channels = await fetch_channels()
    for channel in channels:
        is_member = await check_membership(user_id, channel['id'])
        if not is_member:
            return False
    return True


async def fetch_channels():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/mandatory-users/") as response:
            if response.status == 200:
                data = await response.json()
                print(data)
                return data
            else:
                logger.error(f"Failed to fetch channels: {response.status}")
                return []


async def check_membership(user_id: int, channel_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Error checking membership for channel_id {channel_id}: {e}")
        return False
