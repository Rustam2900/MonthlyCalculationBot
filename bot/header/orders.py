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
        # Foydalanuvchi barcha kanallarga obuna bo'lgan
        buttons = await beck_days_buttons()
        await state.set_state(WorkingStates.waiting_for_working_days)
        await callback_query.message.edit_text("Mehnat ta'tili davomiyligini tanlang:", reply_markup=buttons)
    else:
        # Obuna bo'lmagan kanallarga tugmalar yaratish
        unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
        buttons = await create_channels_buttons(unsubscribed_channels)
        await callback_query.message.edit_text(
            bold("Iltimos, barcha kanallarga obuna bo'ling!"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=buttons
        )


# Ta'til kunlari tanlanganidan keyingi callback
@router.callback_query(lambda callback_query: callback_query.data in ['24days', '36days', '48days'])
async def process_days(callback_query: types.CallbackQuery, state: FSMContext):
    selected_days = int(callback_query.data[:-4])
    await state.update_data(selected_days=selected_days)
    await state.set_state(WorkingStates.same_salary_question)

    # Bir xil oylikmi yoki yo'qligini so'raymiz
    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ha", callback_data="yes_same_salary")],
        [InlineKeyboardButton(text="Yo'q", callback_data="no_same_salary")]
    ])

    await callback_query.message.edit_text(
        "12 oy davomida bir xil miqdorda maosh oldingizmi?",
        reply_markup=buttons
    )


# Bir xil oylik savoliga javobni qabul qilish
@router.callback_query(lambda callback_query: callback_query.data in ['yes_same_salary', 'no_same_salary'])
async def process_salary_question(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'yes_same_salary':
        await state.set_state(WorkingStates.waiting_for_total_salary)
        await callback_query.message.edit_text("Umumiy oyligingizni kiriting (so'mda):")
    else:
        await state.update_data(month=8)  # Avgust oyi bilan boshlaymiz
        await state.set_state(WorkingStates.waiting_for_monthly_salary)
        await callback_query.message.edit_text("Avgust oyi qancha oylik oldingiz? (so'mda):")


# Bir xil oylik bo'lsa umumiy maoshni qabul qilish
@router.message(WorkingStates.waiting_for_total_salary)
async def process_total_salary(message: types.Message, state: FSMContext):
    try:
        # Kiritilgan summani float formatida olamiz va bo'sh joylarni olib tashlaymiz
        total_salary = float(message.text.replace(" ", ""))
        data = await state.get_data()
        selected_days = data['selected_days']  # Foydalanuvchi tanlagan kunlar soni

        # Ta'til pulini hisoblash logikasi
        # Kiritilgan oylikdan jami ta'til puli hisoblanadi
        oppiska = (total_salary * selected_days) * float(0.9449 / 30)  # 30 kunlik oylik asosida foiz hisoblaymiz
        qolgan_summasi = oppiska * 0.87  # Qo'lga tegadigan summa (87%)

        # Foydalanuvchiga natija ko'rsatish
        await message.answer(f"💰 Sizning jami mehnat ta'tili pulingiz (Начисления): {oppiska:.2f} so'm.\n"
                             f"Qo'lga tegishi: {qolgan_summasi:.2f} so'm.")
        await state.clear()  # Stateni tozalash

    except ValueError:
        # Agar foydalanuvchi noto'g'ri ma'lumot kiritsa, ogohlantiramiz
        await message.answer("Iltimos, to'g'ri raqam kiriting.")


# Har oy uchun maosh kiritish jarayoni
@router.message(WorkingStates.waiting_for_monthly_salary)
async def process_monthly_salary(message: types.Message, state: FSMContext):
    monthly_salary = int(message.text)
    data = await state.get_data()
    month = data['month']

    # Har oy uchun kiritilgan maoshni saqlaymiz
    if 'monthly_salaries' not in data:
        data['monthly_salaries'] = {}
    data['monthly_salaries'][month] = monthly_salary

    # Oylar davomida yangilash va siklni tugatish sharti
    if month == 8:  # Avgustni so'rasak, endi sentabrdan dekabrgacha so'raymiz
        month += 1
        await state.update_data(month=month)
        await message.answer(f"{month_name(month)} oyi qancha oylik oldingiz? (so'mda):")
    elif 9 <= month <= 11:  # Sentabr, Oktabr, Noyabr
        month += 1
        await state.update_data(month=month)
        await message.answer(f"{month_name(month)} oyi qancha oylik oldingiz? (so'mda):")
    elif month == 12:  # Dekabrdan keyin yanvargacha qaytamiz
        month = 1
        await state.update_data(month=month)
        await message.answer(f"{month_name(month)} oyi qancha oylik oldingiz? (so'mda):")
    elif 1 <= month < 7:  # Yanvardan iyulgacha davom etamiz
        month += 1
        await state.update_data(month=month)
        await message.answer(f"{month_name(month)} oyi qancha oylik oldingiz? (so'mda):")
    else:  # Iyuldan keyin tugatamiz
        await state.update_data(monthly_salaries=data['monthly_salaries'])
        await process_final_salary(message, state)


# Har bir oy uchun kiritilgan maoshlar asosida ta'til pulini hisoblash
async def process_final_salary(message: types.Message, state: FSMContext):
    data = await state.get_data()
    selected_days = data['selected_days']
    monthly_salaries = data['monthly_salaries']

    # Har oy uchun maoshni jamlaymiz
    total_salary = sum(monthly_salaries.values())

    # Ta'til pulini hisoblash
    oppiska = (total_salary * selected_days) * float(0.9449 / 30)  # Kunlik oppiska
    qolgan_summasi = oppiska * 0.87  # Qo'lga tegadigan summa

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
