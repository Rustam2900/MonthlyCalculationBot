import asyncio
import logging

from aiogram import Router, types, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.markdown import bold

from bot.conustant import START_TEXT
from bot.filters.state import DecreeStates, WorkingStates
from bot.header.api import create_channels_buttons, check_membership, fetch_channels
from bot.keyboard.keybord import home_buttons, category_buttons, confirmation_buttons, beck_buttons, beck_days_buttons

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(lambda callback_query: callback_query.data in ['back'])
async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    channels = await fetch_channels()

    tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
    results = await asyncio.gather(*tasks)

    await bot.answer_callback_query(callback_query.id)

    if all(results):
        buttons = await home_buttons()
        await callback_query.message.edit_text(
            "Xizmatlardan birini tanlang",
            reply_markup=buttons
        )
    else:
        unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
        buttons = await create_channels_buttons(unsubscribed_channels)
        await callback_query.message.edit_text(
            bold(START_TEXT),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=buttons
        )


@router.callback_query(lambda callback_query: callback_query.data in ['high_category'])
async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    channels = await fetch_channels()

    tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
    results = await asyncio.gather(*tasks)

    await bot.answer_callback_query(callback_query.id)

    if all(results):
        buttons = await confirmation_buttons()
        await callback_query.message.edit_text(
            "Xizmatlardan birini tanlang",
            reply_markup=buttons
        )
    else:
        unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
        buttons = await create_channels_buttons(unsubscribed_channels)
        await callback_query.message.edit_text(
            bold(START_TEXT),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=buttons
        )


@router.callback_query(lambda callback_query: callback_query.data in ['decree'])
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback_query.from_user.id
    channels = await fetch_channels()

    tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
    results = await asyncio.gather(*tasks)

    await bot.answer_callback_query(callback_query.id)

    if all(results):
        await state.set_state(DecreeStates.waiting_for_salary)
        await callback_query.message.edit_text("Umumiy oyligingizni jo'nating (Начисления):")
    else:
        unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
        buttons = await create_channels_buttons(unsubscribed_channels)
        await callback_query.message.edit_text(
            bold(START_TEXT),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=buttons
        )


@router.message(DecreeStates.waiting_for_salary)
async def process_salary_input(message: types.Message, state: FSMContext):
    user_input = message.text

    if not user_input.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting.")
        return

    salary = int(user_input)

    decree_money = salary * 4

    await message.answer(f"💰 Sizning jami dekret pulingiz: {decree_money} so'm.")

    buttons = await home_buttons()
    await message.answer("Xizmatlardan birini tanlang", reply_markup=buttons)

    await state.clear()


@router.callback_query(lambda callback_query: callback_query.data in ['working'])
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback_query.from_user.id
    channels = await fetch_channels()

    tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
    results = await asyncio.gather(*tasks)

    await bot.answer_callback_query(callback_query.id)

    if all(results):
        buttons = await beck_days_buttons()
        await state.set_state(WorkingStates.waiting_for_working_days)
        await callback_query.message.edit_text("Mehnat ta'tili davomiyligini tanlang:", reply_markup=buttons)
    else:
        unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
        buttons = await create_channels_buttons(unsubscribed_channels)
        await callback_query.message.edit_text(
            bold(START_TEXT),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=buttons
        )


@router.callback_query(lambda callback_query: callback_query.data in ['24days', '36days', '48days'])
async def process_days(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback_query.from_user.id
    channels = await fetch_channels()

    tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
    results = await asyncio.gather(*tasks)

    await bot.answer_callback_query(callback_query.id)

    if all(results):
        selected_days = int(callback_query.data[:-4])
        await state.update_data(selected_days=selected_days)
        await state.set_state(WorkingStates.same_salary_question)

        buttons = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Ha", callback_data="yes_same_salary")],
            [InlineKeyboardButton(text="Yo'q", callback_data="no_same_salary")]
        ])

        await callback_query.message.edit_text(
            "12 oy davomida bir xil miqdorda maosh oldingizmi?",
            reply_markup=buttons
        )
    else:
        unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
        buttons = await create_channels_buttons(unsubscribed_channels)
        await callback_query.message.edit_text(
            bold(START_TEXT),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=buttons
        )


@router.callback_query(lambda callback_query: callback_query.data in ['yes_same_salary', 'no_same_salary'])
async def process_salary_question(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback_query.from_user.id
    channels = await fetch_channels()

    tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
    results = await asyncio.gather(*tasks)

    await bot.answer_callback_query(callback_query.id)

    if all(results):
        if callback_query.data == 'yes_same_salary':
            await state.set_state(WorkingStates.waiting_for_total_salary)
            await callback_query.message.edit_text("Umumiy oyligingizni kiriting (so'mda):")
        else:
            await state.update_data(month=8)
            await state.set_state(WorkingStates.waiting_for_monthly_salary)
            await callback_query.message.edit_text("Avgust oyi qancha oylik oldingiz? (so'mda):")
    else:
        unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
        buttons = await create_channels_buttons(unsubscribed_channels)
        await callback_query.message.edit_text(
            bold(START_TEXT),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=buttons
        )


@router.message(WorkingStates.waiting_for_total_salary)
async def process_total_salary(message: types.Message, state: FSMContext):
    try:
        total_salary = float(message.text.replace(" ", ""))
        data = await state.get_data()
        selected_days = data['selected_days']

        oppiska = (total_salary * selected_days) * float(0.9449 / 30)
        qolgan_summasi = oppiska * 0.87

        await message.answer(f"💰 Sizning jami mehnat ta'tili pulingiz (Начисления): {oppiska:.2f} so'm.\n"
                             f"Qo'lga tegishi: {qolgan_summasi:.2f} so'm.")
        await state.clear()
    except ValueError:
        await message.answer("Iltimos, to'g'ri raqam kiriting.")


@router.message(WorkingStates.waiting_for_monthly_salary)
async def process_monthly_salary(message: types.Message, state: FSMContext):
    monthly_salary = int(message.text)
    data = await state.get_data()
    month = data['month']

    if 'monthly_salaries' not in data:
        data['monthly_salaries'] = {}
    data['monthly_salaries'][month] = monthly_salary

    if month == 8:
        month += 1
        await state.update_data(month=month)
        await message.answer(f"{month_name(month)} oyi qancha oylik oldingiz? (so'mda):")
    elif 9 <= month <= 11:
        month += 1
        await state.update_data(month=month)
        await message.answer(f"{month_name(month)} oyi qancha oylik oldingiz? (so'mda):")
    elif month == 12:
        month = 1
        await state.update_data(month=month)
        await message.answer(f"{month_name(month)} oyi qancha oylik oldingiz? (so'mda):")
    elif 1 <= month < 7:
        month += 1
        await state.update_data(month=month)
        await message.answer(f"{month_name(month)} oyi qancha oylik oldingiz? (so'mda):")
    else:
        await state.update_data(monthly_salaries=data['monthly_salaries'])
        await process_final_salary(message, state)


async def process_final_salary(message: types.Message, state: FSMContext):
    data = await state.get_data()
    selected_days = data['selected_days']
    monthly_salaries = data['monthly_salaries']

    total_salary = sum(monthly_salaries.values())

    oppiska = (total_salary * selected_days) * float(0.9449 / 30)
    qolgan_summasi = oppiska * 0.87

    await message.answer(f"💰 Sizning jami mehnat ta'tili pulingiz (Начисления): {oppiska:.2f} so'm.\n"
                         f"Qo'lga tegishi: {qolgan_summasi:.2f} so'm.")
    await state.clear()


def month_name(month):
    month_names = {
        1: "Yanvar", 2: "Fevral", 3: "Mart", 4: "Aprel", 5: "May", 6: "Iyun",
        7: "Iyul", 8: "Avgust", 9: "Sentabr", 10: "Oktabr", 11: "Noyabr", 12: "Dekabr"
    }
    return month_names[month]


@router.callback_query(lambda callback_query: callback_query.data in ['primary_class'])
async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
    user_id = callback_query.from_user.id
    channels = await fetch_channels()

    tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
    results = await asyncio.gather(*tasks)

    await bot.answer_callback_query(callback_query.id)

    if all(results):
        buttons = await category_buttons()
        await callback_query.message.edit_text(
            "Xizmatlardan birini tanlang",
            reply_markup=buttons
        )
    else:
        unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
        buttons = await create_channels_buttons(unsubscribed_channels)
        await callback_query.message.edit_text(
            bold(START_TEXT),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=buttons
        )

# @router.callback_query(lambda c: c.data in ['home_education'])
# async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(callback_query.from_user.id, "Salom uyda_talim")
#
#
# @router.callback_query(lambda c: c.data in ['high_class'])
# async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(callback_query.from_user.id, "Salom yuqori_sinf")
#
#
# @router.callback_query(lambda c: c.data in ['primary_class'])
# async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(callback_query.from_user.id, "Salom boshlangich_sinf")
#
#
# @router.callback_query(lambda c: c.data in ['decree'])
# async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(callback_query.from_user.id, "Salom dekret")
#
#
# @router.callback_query(lambda c: c.data in ['working'])
# async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(callback_query.from_user.id, "Salom mehnat_tatili")
