import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.commands import get_main_menu
from handlers.users.notice import main_notice
from utils.db_api import db_commands

from loader import dp

from keyboards.inline import inline_keyboards
from states.all_states import NewEvent, NewTasks, EditEvent


db = db_commands


@dp.message_handler(text='Мероприятия')
async def main_events(message: types.Message, edit=False):
    user_class = await db.check_in_class()
    if not user_class:
        await message.answer('Это доступно только пользователям, которые являются участником класса')
    else:
        user = await db.get_user()
        full_name_user = types.User.get_current().full_name
        await user.update(tg_nickname=full_name_user).apply()

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

                if event.complete_tasks:
                    for task in event.complete_tasks:
                        tasks += f'\n✅ {task}'

                if event.tasks:
                    for task in event.tasks:
                        tasks += f'\n🟡 {task}'
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


@dp.callback_query_handler(text='events:edit')
async def choice_edit_event(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text('Выберите, которое мероприятие вы хотите изменить:',
                                 reply_markup=await inline_keyboards.list_events('edit'))


@dp.callback_query_handler(text_startswith='list_events:edit')
async def send_info_event(call: types.CallbackQuery, event_id=None):
    if event_id:
        id = event_id
    else:
        await call.answer()
        id = str(call.data).split(':')[2]
    event = await db.get_event_by_id(id)

    date = str(event.date).split('-')
    year, month, day = date[0], date[1], date[2]
    list_date = [day, month, year]
    new_date = '.'.join(list_date)

    send_message = f'<u>Информация о меропреятии:</u>' \
                   f'\n\n<b>Название:</b> <i>{event.name}</i>' \
                   f'\n<b>Описани:</b> <i>{event.description}</i>' \
                   f'\n<b>Дата:</b> <i>{new_date}</i>' \
                   f'\n\nВыберите, что хотите изменить:'
    if event_id:
        await call.answer(send_message, reply_markup=inline_keyboards.edit_event(id))
    else:
        await call.message.edit_text(send_message, reply_markup=inline_keyboards.edit_event(id))
    await EditEvent.UniversalState.set()


@dp.callback_query_handler(text_contains='edit_event:name', state=EditEvent.UniversalState)
async def send_message_edit_name(call: types.CallbackQuery, state: FSMContext):
    event_id = str(call.data).split(':')[2]
    event = await db.get_event_by_id(event_id)
    await state.update_data(event=event, edit_field='name')
    await call.message.edit_text('Ввидете новое название:', reply_markup=inline_keyboards.to_main_edit_event(event_id))


@dp.callback_query_handler(text_contains='edit_event:description', state=EditEvent.UniversalState)
async def send_message_edit_name(call: types.CallbackQuery, state: FSMContext):
    event_id = str(call.data).split(':')[2]
    event = await db.get_event_by_id(event_id)
    await state.update_data(event=event, edit_field='description')
    await call.message.edit_text('Ввидете новое описание:',
                                 reply_markup=inline_keyboards.to_main_edit_event(event_id))


@dp.callback_query_handler(text_contains='edit_event:date', state=EditEvent.UniversalState)
async def send_message_edit_name(call: types.CallbackQuery, state: FSMContext):
    event_id = str(call.data).split(':')[2]
    event = await db.get_event_by_id(event_id)
    await state.update_data(event=event, edit_field='date')
    await call.message.edit_text('Ввидете новую дату(пример: "12.04.2020"):',
                                 reply_markup=inline_keyboards.to_main_edit_event(event_id))


@dp.message_handler(state=EditEvent.UniversalState)
async def edit_name_event(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    event = state_data.get('event')
    edit_field = state_data.get('edit_field')

    if message.text == 'Мероприятия':
        await state.reset_state()
        await main_events(message)
    elif message.text == 'Объявления':
        await state.reset_state()
        await main_notice(message)
    elif message.text == 'Главное меню':
        await state.reset_state()
        await get_main_menu(message)
    elif edit_field == 'name':
        event.name = message.text
        await event.update(name=event.name).apply()
        await send_info_event(message, event_id=event.id)
        await state.reset_state()
    elif edit_field == 'description':
        event.description = message.text
        await event.update(description=event.description).apply()
        await send_info_event(message, event_id=event.id)
        await state.reset_state()
    elif edit_field == 'date':
        try:
            enter_date = message.text.split('.')  # 21.12.2021
            day, month, year = int(enter_date[0]), int(enter_date[1]), int(enter_date[2])

            date_event = datetime.date(year, month, day)
            event.date = date_event

            await event.update(date=event.date).apply()
            await send_info_event(message, event_id=event.id)
            await state.reset_state()
        except ValueError or IndexError:
            await message.answer('Вы не правильно ввели дату. Введите заново:')
    else:
        print(edit_field)
        print('fuck you')


@dp.callback_query_handler(text_startswith='to_main_edit_event', state=EditEvent.UniversalState)
async def to_main_edit_event(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    event_id = str(call.data).split(':')[1]
    await send_info_event(call.message, event_id=event_id)


@dp.callback_query_handler(text='bf_edit_event', state=EditEvent.UniversalState)
async def back_from_edit_event(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.reset_state()
    await choice_edit_event(call)


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
        print('thisss')
    event = await db.get_event_by_id(id)

    send_message = '<u>Выбрано мероприятие:</u>'
    print('id of tra:', id)
    name = event.name
    description = event.description

    date = str(event.date).split('-')
    year, month, day = date[0], date[1], date[2]
    list_date = [day, month, year]
    new_date = '.'.join(list_date)
    tasks = '<b>Задания:</b>'

    if event.complete_tasks:
        for task in event.complete_tasks:
            tasks += f'\n✅ {task}'

    if event.tasks:
        for task in event.tasks:
            tasks += f'\n🟡 {task}'
    else:
        tasks += ' Заданий пока нет'

    send_message += f' <i><b>{name}</b></i>\n<b>Описание:</b> {description}\n<b>Дата:</b> {new_date}\n{tasks}'

    await call.message.edit_text(send_message, parse_mode='html', reply_markup=await inline_keyboards.main_task(id))
    await NewTasks.Task.set()


@dp.callback_query_handler(text='back_from_task', state=NewTasks.Task)
async def cancel_delete_event(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.reset_state()
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


@dp.callback_query_handler(text_startswith='main_task:delete', state=NewTasks.Task)
async def choose_task(call: types.CallbackQuery, state: FSMContext):
    await state.reset_state()
    await call.answer()
    id = str(call.data).split(':')[2]
    await call.message.edit_text('Выберите, которое задание вы хотите удалить:',
                                 reply_markup=await inline_keyboards.choose_task_delete(id))


@dp.callback_query_handler(text_startswith='delete_task')
async def delete_task(call: types.CallbackQuery):
    await call.answer()
    task_id = int(str(call.data).split(':')[1])
    event_id = str(call.data).split(':')[2]
    print(event_id)
    event = await db.get_event_by_id(event_id)
    event.tasks.pop(task_id)
    await event.update(tasks=event.tasks).apply()

    await choice_event_tasks(call)


@dp.callback_query_handler(text_startswith='back_from_delete_task')
async def back_from_delete_task(call: types.CallbackQuery):
    await call.answer()
    event_id = str(call.data).split(':')[1]
    await choice_event_tasks(call, event_id=event_id)


@dp.callback_query_handler(text_startswith='main_task:choice_complete', state=NewTasks.Task)
async def choice_complete_tasks(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.reset_state()

    id = str(call.data).split(':')[2]
    await call.message.edit_text('Выберите выполненные задания:',
                                 reply_markup=await inline_keyboards.choice_complete_tasks(id))


@dp.callback_query_handler(text_startswith='cc_tasks')
async def complete_task(call: types.CallbackQuery):
    await call.answer()
    task_id = int(str(call.data).split(':')[1])
    event_id = str(call.data).split(':')[2]
    status = str(call.data).split(':')[3]

    event = await db.get_event_by_id(event_id)

    if status == 'work':
        task = event.tasks.pop(task_id)
        try:
            event.complete_tasks += [task]
        except TypeError:
            event.complete_tasks = [task]
    else:
        task = event.complete_tasks.pop(task_id)
        try:
            event.tasks += [task]
        except TypeError:
            event.tasks = [task]

    await event.update(complete_tasks=event.complete_tasks, tasks=event.tasks).apply()
    await call.message.edit_text('Выберите выполненные задания:',
                                 reply_markup=await inline_keyboards.choice_complete_tasks(event_id))


@dp.callback_query_handler(text_startswith='bf_choice_complete_task')
async def bf_choice_complete_task(call: types.CallbackQuery):
    await call.answer()
    event_id = str(call.data).split(':')[1]
    await choice_event_tasks(call, event_id=event_id)

