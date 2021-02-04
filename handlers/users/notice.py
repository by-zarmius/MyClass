from aiogram import types
from aiogram.dispatcher import FSMContext

from utils.db_api import db_commands

from loader import dp

from keyboards.inline import inline_keyboards
from states.all_states import NewNotice


db = db_commands.DBCommands()


@dp.message_handler(text='Объявления')
async def main_notice(message: types.Message):
    send_message = '<b>Текущие объявлени:</b>'
    notices = await db.get_notice()

    if notices:
        counter = 1
        for notice in notices:
            title = notice.name
            body = notice.body

            send_message += f'\n\n{str(counter)}) <i>{title}</i>\n{body}'
            counter += 1
    else:
        send_message += '\n\n У вас пока нет объявлений.'

    if notices:
        await message.answer(send_message, parse_mode='html', reply_markup=inline_keyboards.notice_buttons)
    else:
        await message.answer(send_message, parse_mode='html', reply_markup=inline_keyboards.no_notice_buttons)


@dp.callback_query_handler(text_contains='notice:add')
async def enter_title_notice(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text('Введите название объявления:')
    await NewNotice.Title.set()


@dp.message_handler(state=NewNotice.Title)
async def complete_enter_title_notice(message: types.Message, state: FSMContext):
    new_notice = db_commands.Notice()
    new_notice.name = message.text
    await state.update_data(new_notice=new_notice)

    await message.answer(f'<b>Заголовок:</b> {message.text}')
    await message.answer('<i>Введите текст объявления:</i>')
    await NewNotice.Body.set()


@dp.message_handler(state=NewNotice.Body)
async def complete_enter_title_notice(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_notice = data.get('new_notice')
    user_class_id = await db.get_id_class()
    new_notice.body = message.text
    new_notice.class_id = int(user_class_id)

    await new_notice.create()
    await state.reset_state()

    await main_notice(message)


@dp.callback_query_handler(text_contains='notice:remove')
async def delete_notice_start(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text('Выберете, которое объявление вы желаете удалить:',
                              reply_markup=await inline_keyboards.delete_notice())


@dp.callback_query_handler(text_contains='delete_notice')
async def delete_notice(call: types.CallbackQuery):
    await call.answer()
    id = call.data.split(':')[1]

    notice = await db.get_notice_by_id(int(id))
    await notice.delete()

    send_message = '<b>Текущие объявлени:</b>'
    notices = await db.get_notice()

    if notices:
        counter = 1
        for notice in notices:
            title = notice.name
            body = notice.body

            send_message += f'\n\n{str(counter)}) <i>{title}</i>\n{body}'
            counter += 1
    else:
        send_message += '\n\n У вас пока нет объявлений.'

    if notices:
        await call.message.edit_text(send_message, parse_mode='html', reply_markup=inline_keyboards.notice_buttons)
    else:
        await call.message.edit_text(send_message, parse_mode='html', reply_markup=inline_keyboards.no_notice_buttons)


@dp.callback_query_handler(text='back_from_notice')
async def back_to_notices(call: types.CallbackQuery):
    send_message = '<b>Текущие объявлени:</b>'
    notices = await db.get_notice()

    if notices:
        counter = 1
        for notice in notices:
            title = notice.name
            body = notice.body

            send_message += f'\n\n{str(counter)}) <i>{title}</i>\n{body}'
            counter += 1
    else:
        send_message += '\n\n У вас пока нет объявлений.'

    if notices:
        await call.message.edit_text(send_message, parse_mode='html', reply_markup=inline_keyboards.notice_buttons)
    else:
        await call.message.edit_text(send_message, parse_mode='html', reply_markup=inline_keyboards.no_notice_buttons)