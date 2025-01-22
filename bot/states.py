from aiogram.fsm.state import StatesGroup, State


class UserForm(StatesGroup):
    article = State()
