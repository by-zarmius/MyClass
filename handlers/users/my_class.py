from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.deep_linking import get_start_link

from utils.db_api import db_commands

from loader import dp

from keyboards.default import main_keyboard
from keyboards.inline import inline_keyboards
from states.all_states import MyClass


db = db_commands


@dp.message_handler(text='Мой класс')
async def my_class(message: types.Message, edit=False):
    user = await db.get_user()
    full_name_user = types.User.get_current().full_name
    await user.update(tg_nickname=full_name_user).apply()

    try:
        user_class = await db.get_class()
    except IndexError:
        user_class = await db.check_in_class()
    if user_class:

        events = await db.get_event()
        notices = await db.get_notice()

        count_members = len(user_class.members)
        tg_chat = user_class.telegram_chat
        join_class = await get_start_link(f'to_{user_class.id}', encode=True)
        if not tg_chat:
            tg_chat = 'Нет'
        send_message = f'<u>Инфомарция о классе:</u>' \
                       f'\n\n<b>Название:</b> {user_class.name}' \
                       f'\n<b>Код класса:</b> {user_class.id}' \
                       f'\n<b>Количество участников:</b> {count_members}' \
                       f'\n<b>Чат класса:</b> {tg_chat}' \
                       f'\n<b>Ссылка на присоединение:</b> {join_class}' \
                       f'\n<i>* Для того, чтобы узнать как другие люди могут присоедениться к вашему классу отправьте команду /how_join_class</i>' \

        message_events = '\n\n<u>Активные мероприятия:</u>'

        if events:
            counter = 1
            for event in events:
                name = event.name
                description = event.description

                date = str(event.date).split('-')
                year, month, day = date[0], date[1], date[2]
                list_date = [day, month, year]
                new_date = '.'.join(list_date)

                message_events += f'\n\n{str(counter)}) <i><b>{name}</b></i>\n<b>Описание:</b> {description}\n<b>Дата:</b> {new_date}'
                counter += 1
        else:
            message_events += '\n\nНет актуальных мероприятий...'
        send_message += message_events

        message_notices = '\n\n<b>Текущие объявлени:</b>'
        if notices:
            counter = 1
            for notice in notices:
                title = notice.name
                body = notice.body

                message_notices += f'\n\n{str(counter)}) <i>{title}</i>\n{body}'
                counter += 1
        else:
            message_notices += '\n\n У вас пока нет объявлений.'

        send_message += message_notices

        if not edit:
            await message.answer(send_message,
                                 reply_markup=inline_keyboards.edit_class(),
                                 disable_web_page_preview=True)
        else:
            await message.edit_text(send_message,
                                    reply_markup=inline_keyboards.edit_class(),
                                    disable_web_page_preview=True)

    else:
        await message.answer('Вы не являетесь участником какого-либо класса. Создайте новый '
                             'или присоединитесь к уже существующему',
                             reply_markup=main_keyboard.without_class)


@dp.callback_query_handler(text='my_class:view_members')
async def view_members(call: types.CallbackQuery):
    await call.answer()
    send_message = 'Список участников чата:\n'
    user_class = await db.get_class()

    counter = 1
    for member in user_class.members:
        user = await db.get_user_by_tg_id(member)
        name = user.tg_nickname
        if user.name:
            name = user.name
        send_message += f'\n{counter}) <a href="tg://user?id={member}">{name}</a>'
        counter += 1

    await call.message.edit_text(send_message, reply_markup=inline_keyboards.to_my_class)


@dp.callback_query_handler(text='to_my_class')
async def to_my_class(call: types.CallbackQuery):
    await call.answer()
    await my_class(call.message, edit=True)


@dp.callback_query_handler(text='my_class:edit')
async def edit_class(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text('Что вы хотите изменить?',
                                 reply_markup=inline_keyboards.edit_info_class())


@dp.callback_query_handler(text='edit_class:name')
async def message_edit_name_class(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text('Введите новое название класса:')
    await MyClass.Name.set()


@dp.message_handler(state=MyClass.Name)
async def edit_name_class(message: types.Message, state: FSMContext):
    user_class = await db.get_class()
    user_class.name = message.text
    await user_class.update(name=user_class.name).apply()
    await state.reset_state()

    await my_class(message)


@dp.callback_query_handler(text='edit_class:tg_chat')
async def message_edit_chat_class(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text('Отправьте ссылку на чат:')
    await MyClass.PinCat.set()


@dp.message_handler(state=MyClass.PinCat)
async def edit_chat_class(message: types.Message, state: FSMContext):
    user_class = await db.get_class()
    user_class.telegram_chat = message.text
    await user_class.update(telegram_chat=user_class.telegram_chat).apply()
    await state.reset_state()

    await my_class(message)
