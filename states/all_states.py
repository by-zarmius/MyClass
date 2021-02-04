from aiogram.dispatcher.filters.state import StatesGroup, State


class NewClass(StatesGroup):
    Name = State()
    Chat = State()


class NewNotice(StatesGroup):
    Title = State()
    Body = State()
