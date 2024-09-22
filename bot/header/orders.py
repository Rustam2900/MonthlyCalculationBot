import asyncio
import logging

from aiogram import Router, types, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import bold

from bot.conustant import START_TEXT
from bot.filters.state import DecreeStates, WorkingStates, SalaryStates
from bot.header.api import create_channels_buttons, check_membership, fetch_channels
from bot.keyboard.keybord import home_buttons, category_buttons, confirmation_buttons, beck_days_buttons, beck_buttons

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


# @router.callback_query(lambda callback_query: callback_query.data in ['high_category'])
# async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
#     user_id = callback_query.from_user.id
#     channels = await fetch_channels()
#
#     tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
#     results = await asyncio.gather(*tasks)
#
#     await bot.answer_callback_query(callback_query.id)
#
#     if all(results):
#         buttons = await confirmation_buttons()
#         await callback_query.message.edit_text(
#             "Xizmatlardan birini tanlang",
#             reply_markup=buttons
#         )
#     else:
#         unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
#         buttons = await create_channels_buttons(unsubscribed_channels)
#         await callback_query.message.edit_text(
#             bold(START_TEXT),
#             parse_mode=ParseMode.MARKDOWN,
#             reply_markup=buttons
#         )


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

        await callback_query.message.edit_text(
            "12 oy davomida bir xil miqdorda maosh oldingizmi?",
            reply_markup=await confirmation_buttons()
        )
    else:
        unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
        buttons = await create_channels_buttons(unsubscribed_channels)
        await callback_query.message.edit_text(
            bold(START_TEXT),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=buttons
        )


@router.callback_query(lambda callback_query: callback_query.data in ['yes', 'no'])
async def process_salary_question(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback_query.from_user.id
    channels = await fetch_channels()

    tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
    results = await asyncio.gather(*tasks)

    await bot.answer_callback_query(callback_query.id)

    if all(results):
        if callback_query.data == 'yes':
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
async def process_callback(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    user_id = callback_query.from_user.id
    channels = await fetch_channels()

    tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
    results = await asyncio.gather(*tasks)

    await bot.answer_callback_query(callback_query.id)

    if all(results):
        buttons = await category_buttons()
        await callback_query.message.edit_text(
            "Toifangizni tanlang:",
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
async def process_callback(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext, message: types.Message):
    user_id = callback_query.from_user.id
    channels = await fetch_channels()

    tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
    results = await asyncio.gather(*tasks)

    await bot.answer_callback_query(callback_query.id)

    if all(results):
        user_input = message.text
        if not user_input.isdigit():
            await message.answer("Iltimos, faqat raqam kiriting.")
            return
        await state.update_data(teaching_hours=int(user_input))
        await state.set_state(SalaryStates.teaching_hours)
        await callback_query.message.answer(
            "Boshlang'ich sinfga 1 haftada necha soat dars o'tasiz? Raqamlarda yuboring:",
            reply_markup=await beck_buttons())

    else:
        unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
        buttons = await create_channels_buttons(unsubscribed_channels)
        await callback_query.message.edit_text(
            bold(START_TEXT),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=buttons
        )


@router.message(SalaryStates.teaching_hours)
async def enter_teaching_hours(message: types.Message, state: FSMContext):
    await state.update_data(teaching_hours=int(message.text))
    await state.set_state(SalaryStates.class_supervisor)
    await message.answer("Sinf rahbarimisiz? (Ha/Yo'q)")


@router.message(SalaryStates.class_supervisor)
async def class_supervisor_answer(message: types.Message, state: FSMContext):
    is_supervisor = message.text.lower() == "ha"
    await state.update_data(class_supervisor=is_supervisor)
    await state.set_state(SalaryStates.number_of_students)
    await message.answer("Sinfingizdagi o'quvchilar sonini kiriting :")


@router.message(SalaryStates.number_of_students)
async def enter_number_of_students(message: types.Message, state: FSMContext):
    await state.update_data(number_of_students=message.text)
    await state.set_state(SalaryStates.check_notebooks)
    await message.answer("Daftar tekshirasizmi? (Ha/Yo'q)")


@router.message(SalaryStates.check_notebooks)
async def check_notebooks_answer(message: types.Message, state: FSMContext):
    checks_notebooks = message.text.lower() == "ha"
    await state.update_data(check_notebooks=checks_notebooks)
    await state.set_state(SalaryStates.notebooks_checked)
    await message.answer("Necha nafar o'quvchi daftari tekshiriladi? Raqamlarda kiriting:")


@router.message(SalaryStates.notebooks_checked)
async def enter_notebooks_checked(message: types.Message, state: FSMContext):
    await state.update_data(notebooks_checked=int(message.text))
    await state.set_state(SalaryStates.additional_duties)
    await message.answer("Kabinet mudirlik vazifasi ham bormi? (Ha/Yo'q)")


@router.message(SalaryStates.additional_duties)
async def additional_duties_answer(message: types.Message, state: FSMContext):
    additional_duties = message.text.lower() == "ha"
    await state.update_data(additional_duties=additional_duties)
    await state.set_state(SalaryStates.bonus_percentage)
    await message.answer("Ustama foizi (barcha sertifikatlar foizi yig'indisi) Raqamlarda kiriting:")


@router.message(SalaryStates.bonus_percentage)
async def enter_bonus_percentage(message: types.Message, state: FSMContext):
    await state.update_data(bonus_percentage=float(message.text))
    await state.set_state(SalaryStates.calculate_salary)
    await message.answer("Hisob-kitobni boshlaymizmi? (Ha/Yo'q)")


@router.message(SalaryStates.calculate_salary)
async def calculate_salary(message: types.Message, state: FSMContext):
    if message.text.lower() == "ha":
        data = await state.get_data()
        teaching_hours = data['teaching_hours']
        is_supervisor = data['class_supervisor']
        number_of_students = int(data['number_of_students'].split('-')[0])  # e.g., "1-15" -> 1
        checks_notebooks = data['check_notebooks']
        notebooks_checked = data['notebooks_checked']
        additional_duties = data['additional_duties']
        bonus_percentage = data['bonus_percentage']

        base_rate = 100000  # Example base rate per hour
        salary = teaching_hours * base_rate

        if is_supervisor:
            salary += 50000  # Example additional pay for being a supervisor
        salary += number_of_students * 10000  # Example additional pay per student
        if checks_notebooks:
            salary += notebooks_checked * 5000  # Example additional pay per notebook checked
        if additional_duties:
            salary += 20000  # Example additional pay for additional duties
        salary += (salary * bonus_percentage / 100)  # Apply bonus percentage

        await message.answer(f"Sizning jami oylik maoshingiz: {salary:.2f} so'm")
    else:
        await message.answer("Hisoblashdan voz kechildi.")
    await state.clear()

# @router.callback_query(lambda callback_query: callback_query.data in ['high_class'])
# async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
#     user_id = callback_query.from_user.id
#     channels = await fetch_channels()
#
#     tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
#     results = await asyncio.gather(*tasks)
#
#     await bot.answer_callback_query(callback_query.id)
#
#     if all(results):
#         buttons = await category_buttons()
#         await callback_query.message.edit_text(
#             "Xizmatlardan birini tanlang",
#             reply_markup=buttons
#         )
#     else:
#         unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
#         buttons = await create_channels_buttons(unsubscribed_channels)
#         await callback_query.message.edit_text(
#             bold(START_TEXT),
#             parse_mode=ParseMode.MARKDOWN,
#             reply_markup=buttons
#         )
#
#
# @router.callback_query(lambda callback_query: callback_query.data in ['home_education'])
# async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
#     user_id = callback_query.from_user.id
#     channels = await fetch_channels()
#
#     tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
#     results = await asyncio.gather(*tasks)
#
#     await bot.answer_callback_query(callback_query.id)
#
#     if all(results):
#         buttons = await category_buttons()
#         await callback_query.message.edit_text(
#             "Xizmatlardan birini tanlang",
#             reply_markup=buttons
#         )
#     else:
#         unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
#         buttons = await create_channels_buttons(unsubscribed_channels)
#         await callback_query.message.edit_text(
#             bold(START_TEXT),
#             parse_mode=ParseMode.MARKDOWN,
#             reply_markup=buttons
#         )
#
#
# @router.callback_query(lambda callback_query: callback_query.data in ['soatbay'])
# async def process_callback(callback_query: types.CallbackQuery, bot: Bot):
#     user_id = callback_query.from_user.id
#     channels = await fetch_channels()
#
#     tasks = [check_membership(user_id, channel['channel_id']) for channel in channels]
#     results = await asyncio.gather(*tasks)
#
#     await bot.answer_callback_query(callback_query.id)
#
#     if all(results):
#         buttons = await category_buttons()
#         await callback_query.message.edit_text(
#             "Xizmatlardan birini tanlang",
#             reply_markup=buttons
#         )
#     else:
#         unsubscribed_channels = [channel for channel, result in zip(channels, results) if not result]
#         buttons = await create_channels_buttons(unsubscribed_channels)
#         await callback_query.message.edit_text(
#             bold(START_TEXT),
#             parse_mode=ParseMode.MARKDOWN,
#             reply_markup=buttons
#         )
