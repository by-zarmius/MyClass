from aiogram import types
from aiogram.dispatcher import FSMContext

from utils.db_api import db_commands

from loader import dp

from keyboards.default import main_keyboard
from keyboards.inline import inline_keyboards
from states.all_states import NewEvent, NewTasks


db = db_commands.DBCommands()


@dp.message_handler(text='ДЗ')
async def main_ht(message: types.Message):
    await message.answer('Выберите действие:', reply_markup=main_keyboard.home_tasks_main)