from aiogram import types
from aiogram.dispatcher import FSMContext

from utils.db_api import db_commands

from loader import dp

from keyboards.default import main_keyboard
from keyboards.inline import inline_keyboards


db = db_commands


@dp.message_handler(text='ДЗ')
async def main_ht(message: types.Message):
    user_class = await db.check_in_class()
    if not user_class:
        await message.answer('Это доступно только пользователям, которые являются участником класса')
    else:
        user = await db.get_user()
        full_name_user = types.User.get_current().full_name
        await user.update(tg_nickname=full_name_user).apply()

        await message.answer('Выберите действие:', reply_markup=main_keyboard.home_tasks_main)


@dp.message_handler(text='Добавить')
async def choice_subject(message: types.Message):
    user_class = await db.check_in_class()
    if not user_class:
        await message.answer('Это доступно только пользователям, которые являются участником класса')
    else:
        await message.answer('Выберите предмет к которому хотите добавить дз:',
                             reply_markup=await inline_keyboards.choice_subject())


@dp.callback_query_handler(text_startswith='choice_subject')
async def choice_data(call: types.CallbackQuery):
    subject = str(call.data).split(':')[1]
    await call.message.edit_text('Выберите на которое число вы хотите добавить дз',
                                 reply_markup=await inline_keyboards.choice_date(subject))
