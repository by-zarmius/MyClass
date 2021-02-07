import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.commands import get_main_menu
from handlers.users.notice import main_notice
from utils.db_api import db_commands

from loader import dp

from keyboards.inline import inline_keyboards
from states.all_states import NewEvent, NewTasks


db = db_commands.DBCommands()


@dp.message_handler(text='Мероприятия')
async def main_events(message: types.Message, edit=False):
    send_message = '<u>Активные мероприятия:</u>'
    events = await db.get_event()

    if events:
        counter = 1
        for event in events:
            name = event.name
            description = event.description

            date = str(event.date).split('-')
            year, month, day = date[0], date[1], date[2]
            list_date = [day, month, year]
            new_date = '.'.join(list_date)
            tasks = '<b>Задания:</b>'

            if event.tasks:
                for task in event.tasks:
                    tasks += f'\n- {task}'
            else:
                tasks += ' Заданий пока нет'

            send_message += f'\n\n{str(counter)}) <i><b>{name}</b></i>\n<b>Описание:</b> {description}\n<b>Дата:</b> {new_date}\n{tasks}'
            counter += 1
    else:
        send_message += '\n\nНет актуальных мероприятий...'

    if not edit:
        if events:
            await message.answer(send_message, reply_markup=inline_keyboards.events_buttons)
        else:
            await message.answer(send_message, reply_markup=inline_keyboards.no_events_buttons)
    else:
        if events:
            await message.edit_text(send_message, reply_markup=inline_keyboards.events_buttons)
        else:
            await message.edit_text(send_message, reply_markup=inline_keyboards.no_events_buttons)


@dp.callback_query_handler(text='events:add')
async def create_event(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer('Ввведите название мероприятия:')
    await NewEvent.Name.set()


@dp.message_handler(state=NewEvent.Name)
async def create_event_name(message: types.Message, state: FSMContext):
    await message.answer(f'Название: {message.text}')
    event = db_commands.Events()
    event.name = message.text
    await state.update_data(event=event)
    await message.answer('Введите на которую дату запланировано мероприятие(в формате "12.04.2020")')
    await NewEvent.Date.set()


@dp.message_handler(state=NewEvent.Date)
async def create_event_date(message: types.Message, state: FSMContext):
    data = await state.get_data()
    event = data.get('event')


    try:
        enter_date = message.text.split('.')  # 21.12.2021
        day, month, year = int(enter_date[0]), int(enter_date[1]), int(enter_date[2])

        date_event = datetime.date(year, month, day)
        user_class_id = await db.get_id_class()

        event.date = date_event
        event.class_id = int(user_class_id)

        await state.update_data(event=event)
        await NewEvent.Description.set()
        await message.answer('Введите описание мероприятия:')
    except ValueError or IndexError:
        await message.answer('Вы не правильно ввели дату. Введите заново:')


@dp.message_handler(state=NewEvent.Description)
async def create_event_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    event = data.get('event')

    event.description = message.text

    await state.update_data(event=event)
    await message.answer('Хотите ли вы добавить задания к мероприятию(потом вы также сможете это сделать)?',
                         reply_markup=inline_keyboards.event_create_task)


@dp.callback_query_handler(text='event_create_tasks:no', state=NewEvent.Description)
async def complete_create_event(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    event = data.get('event')
    await event.create()

    await state.reset_state()
    await main_events(call.message, edit=True)


@dp.callback_query_handler(text='event_create_tasks:yes', state=NewEvent.Description)
async def create_event_add_tasks(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите текст задания:')
    await NewEvent.NewTask.set()


@dp.message_handler(state=NewEvent.NewTask)
async def create_task_for_event(message: types.Message, state: FSMContext, edit_tasks=False):
    data = await state.get_data()
    event = data.get('event')
    try:
        event.tasks += [message.text]
    except:
        event.tasks = [message.text]

    send_message = f'К мероприяютию: <i>{event.name}</i> привязаны следующие задания:'
    for task in event.tasks:
        send_message += f'\n- {task}'

    send_message += '\n\n<b>Продолжайте писать ещё задания или нажмите "Закончить"</b>'

    await state.update_data(event=event)

    if not edit_tasks:
        await message.answer(send_message, reply_markup=inline_keyboards.event_add_more_task)
    else:
        await message.answer(send_message, reply_markup=inline_keyboards.event_end_enter_tasks)


@dp.callback_query_handler(text='end_enter_task_for_event', state=NewEvent.NewTask)
async def end_create_event(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    event = data.get('event')
    await event.create()

    await state.reset_state()
    await main_events(call.message, edit=True)


@dp.callback_query_handler(text='events:remove')
async def main_delete_event(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text('Выберите, которое мероприятие вы хотите удалить:',
                                 reply_markup=await inline_keyboards.list_events('delete'))


@dp.callback_query_handler(text_startswith='list_events:delete')
async def choice_delete_event(call: types.CallbackQuery):
    await call.answer()
    data = str(call.data)
    id = data.split(':')[2]
    event = await db.get_event_by_id(id)

    await call.message.edit_text(f'Вы уверены, что хотите удалить мероприятие: <i>{event.name}</i>',
                              reply_markup=await inline_keyboards.check_delete_event(id))


@dp.callback_query_handler(text_startswith='check_remove_event:yes')
async def confirm_delete_event(call: types.CallbackQuery):
    await call.answer()
    event_id = str(call.data).split(':')[2]
    event = await db.get_event_by_id(event_id)
    await event.delete()

    await main_events(call.message, edit=True)


@dp.callback_query_handler(text_startswith='check_remove_event:no')
async def cancel_delete_event(call: types.CallbackQuery):
    await call.answer()
    await main_events(call.message, edit=True)


@dp.callback_query_handler(text='back_from_event')
async def cancel_delete_event(call: types.CallbackQuery):
    await call.answer()
    await main_events(call.message, edit=True)


@dp.callback_query_handler(text='events:tasks')
async def main_tasks(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text('Выберите с каким мероприятием вы хотите работать:',
                                 reply_markup=await inline_keyboards.list_events('tasks'))


@dp.callback_query_handler(text_startswith='list_events:tasks')
async def choice_event_tasks(call: types.CallbackQuery, event_id=None):
    await call.answer()
    try:
        id = str(call.data).split(':')[2]
    except IndexError:
        id = event_id
    event = await db.get_event_by_id(id)

    send_message = '<u>Выбрано мероприятие:</u>'

    name = event.name
    description = event.description

    date = str(event.date).split('-')
    year, month, day = date[0], date[1], date[2]
    list_date = [day, month, year]
    new_date = '.'.join(list_date)
    tasks = '<b>Задания:</b>'

    if event.tasks:
        for task in event.tasks:
            tasks += f'\n- {task}'
    else:
        tasks += ' Заданий пока нет'

    send_message += f' <i><b>{name}</b></i>\n<b>Описание:</b> {description}\n<b>Дата:</b> {new_date}\n{tasks}'

    await call.message.edit_text(send_message, parse_mode='html', reply_markup=await inline_keyboards.main_task(id))
    await NewTasks.Task.set()


@dp.callback_query_handler(text='back_from_task')
async def cancel_delete_event(call: types.CallbackQuery):
    await call.answer()
    await main_tasks(call)


@dp.callback_query_handler(text_startswith='main_task:add', state=NewTasks.Task)
async def main_task_add(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    id = str(call.data).split(':')[2]
    event = await db.get_event_by_id(id)

    await state.update_data(event=event, create=True)
    await call.message.edit_text('Введите название задания:')


@dp.message_handler(state=NewTasks.Task)
async def new_task(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    create = state_data.get('create')
    print(create, type(create))
    if message.text == 'Главное меню':
        await state.reset_state()
        await get_main_menu(message)
    elif message.text == 'Объявления':
        await state.reset_state()
        await main_notice(message)
    elif message.text == 'Мероприятия':
        await state.reset_state()
        await main_events(message)
    elif create:
        await create_task_for_event(message, state, edit_tasks=True)
    else:
        pass


@dp.callback_query_handler(text='to_event_detail', state=NewTasks.Task)
async def end_add_task(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    state_data = await state.get_data()
    event = state_data.get('event')
    await event.update(tasks=event.tasks).apply()
    await choice_event_tasks(call, event_id=event.id)


# @dp.callback_query_handler()
# async def cancel_delete_event(call: types.CallbackQuery):
#     await call.answer()
#     print(call.data)