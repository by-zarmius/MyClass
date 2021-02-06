from aiogram.dispatcher.filters.state import StatesGroup, State


class NewClass(StatesGroup):
    Name = State()
    Chat = State()


class NewNotice(StatesGroup):
    Title = State()
    Body = State()


class NewEvent(StatesGroup):
    Name = State()
    Date = State()
    Description = State()
    NewTask = State()


class NewTasks(StatesGroup):
    Task = State()


class NewSchedule(StatesGroup):
    Schedule = State()

