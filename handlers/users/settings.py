from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.commands import get_main_menu
from utils.db_api import db_commands

from loader import dp

from keyboards.default import main_keyboard
from keyboards.inline import inline_keyboards
from states.all_states import EditUserName


db = db_commands


@dp.message_handler(text='Настройки')
async def main_settings(message: types.Message):
    await message.answer('Выберите действие:', reply_markup=main_keyboard.settings_buttons)


@dp.message_handler(text='Изменить имя')
async def message_edit_name_user(message: types.Message):
    user = await db.get_user()
    if user.name:
        await message.answer(f'Вас зовут: {user.name}', reply_markup=inline_keyboards.edit_user_name())
    else:
        await message.answer('Вы не добавили своего настоящего имени. '
                             'Это нужно для того, чтобы другие участники '
                             'вашего класса могли быстро узнать вас.',
                             reply_markup=inline_keyboards.edit_user_name())


@dp.callback_query_handler(text='user:edit_name')
async def edit_name_user(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text('Введите ваше имя:')
    await EditUserName.UserName.set()


@dp.message_handler(state=EditUserName.UserName)
async def save_new_user_name(message: types.Message, state: FSMContext):
    if message.text == 'Изменить имя':
        await state.reset_state()
        await message_edit_name_user(message)
    elif message.text == 'Выйти из класса':
        await state.reset_state()
        await message_exit_from_class(message)
    elif message.text == 'Главное меню':
        await state.reset_state()
        await get_main_menu(message)
    else:
        user = await db.get_user()
        user.name = message.text
        await user.update(name=user.name).apply()
        await message.answer(f'Ваше имя успешно изменено на: {message.text}')
        await state.reset_state()


@dp.message_handler(text='Выйти из класса')
async def message_exit_from_class(message: types.Message):
    user_class = await db.get_class()
    await message.answer(f'Вы уверены, что хотите выйти из класса: {user_class.name}',
                         reply_markup=inline_keyboards.exit_from_class())


@dp.callback_query_handler(text='exit_from_class:yes')
async def exit_from_class(call: types.CallbackQuery):
    await call.answer()
    user_class = await db.get_class()
    user = types.User.get_current().id
    user_class.members.remove(user)
    await user_class.update(members=user_class.members).apply()
    await get_main_menu(call.message)


@dp.callback_query_handler(text='exit_from_class:no')
async def cancel_exit_from_class(call: types.CallbackQuery):
    await call.answer()
    await get_main_menu(call.message)
