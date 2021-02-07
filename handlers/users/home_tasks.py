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


@dp.message_handler(text='Добавить')
async def choice_subject(message: types.Message):
    await message.answer('Выберите предмет к которому хотите добавить дз:',
                         reply_markup=await inline_keyboards.choice_subject())


@dp.callback_query_handler(text_startswith='choice_subject')
async def choice_data(call: types.CallbackQuery):
    subject = str(call.data).split(':')[1]
    await call.message.edit_text('Выберите на которое число вы хотите добавить дз',
                                 reply_markup=await inline_keyboards.choice_date(subject))
