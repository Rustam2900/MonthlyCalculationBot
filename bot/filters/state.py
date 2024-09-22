from aiogram.fsm.state import StatesGroup, State


class DecreeStates(StatesGroup):
    waiting_for_salary = State()


class WorkingStates(StatesGroup):
    waiting_for_working_days = State()  # 24, 36, yoki 48 kunga tanlash
    same_salary_question = State()  # Bir xil oylikmi yo'qmi so'raladi
    waiting_for_total_salary = State()  # Bir xil bo'lsa, umumiy maosh
    waiting_for_monthly_salary = State()  # Har oy alohida maosh


class SalaryStates(StatesGroup):
    selecting_hours = State()
    checking_class_leader = State()
    selecting_students = State()
    check_notebook = State()
    selecting_students_notebook = State()
    role_cabinets = State()
    certificates_sum = State()
    salary_sum = State()
    calculating_salary = State()
