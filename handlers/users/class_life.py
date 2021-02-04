from aiogram import types
from aiogram.dispatcher import FSMContext

from utils.db_api import db_commands

from loader import dp

from keyboards.default import main_keyboard
from keyboards.inline import inline_keyboards


@dp.message_handler(text='Жизнь класса')
async def class_life(message: types.Message):
    await message.answer('Выберите раздел:', reply_markup=main_keyboard.class_life)
