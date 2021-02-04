from aiogram import types
from aiogram.dispatcher import FSMContext

from utils.db_api import db_commands

from loader import dp

from keyboards.inline import inline_keyboards
from states.all_states import NewNotice


db = db_commands.DBCommands()


@dp.message_handler(text='Мероприятия')
async def main_events(message: types.Message):
    send_message = 'Активные мероприятия:'

    await message.answer(send_message, reply_markup=)
