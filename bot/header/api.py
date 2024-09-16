import logging

import aiohttp
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot

from bot.conustant import TEXT_

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
        [InlineKeyboardButton(text=TEXT_, callback_data="check_subscription")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def check_user_subscription(user_id):
    channels = fetch_channels()

    for channel in channels:
        is_member = await check_membership(user_id, channel['channel_id'])
        if not is_member:
            return False
    return True


def fetch_channels():
    response = aiohttp.get(BASE_URL)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch channels: {response.status_code}")
        return []


async def check_membership(user_id: int, channel_id: int, bot: Bot) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logging.error(f"Error checking membership for channel_id {channel_id}: {e}")
        return False


async def check_user_registration(session, telegram_id):
    url = f"{BASE_URL}/user/{telegram_id}"
    async with session.get(url) as response:
        print(f"User registration check URL: {url}")
        print(f"User registration check response status: {response.status}")
        return response.status == 200
