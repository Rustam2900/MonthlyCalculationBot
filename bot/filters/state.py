from aiogram.fsm.state import StatesGroup, State


class DecreeStates(StatesGroup):
    waiting_for_salary = State()


class WorkingStates(StatesGroup):
    waiting_for_working_days = State()  # 24, 36, yoki 48 kunga tanlash
    same_salary_question = State()      # Bir xil oylikmi yo'qmi so'raladi
    waiting_for_total_salary = State()  # Bir xil bo'lsa, umumiy maosh
    waiting_for_monthly_salary = State()  # Har oy alohida maosh
