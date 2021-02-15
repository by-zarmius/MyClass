import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.users.commands import get_main_menu
from utils.db_api import db_commands

from loader import dp

from keyboards.default import main_keyboard
from keyboards.inline import inline_keyboards
from states.all_states import HomeTasks


db = db_commands


def get_dict_home_tasks(list_home_tasks):
    dict_home_tasks = {}

    for task in list_home_tasks:
        date = task.date
        date = str(date).split('-')
        year_date, month_date, day_date = date[0], date[1], date[2]
        list_date = [day_date, month_date, year_date]
        new_date = '.'.join(list_date)
        if new_date not in dict_home_tasks:

            dict_home_tasks[new_date] = [task]
        else:
            dict_home_tasks[new_date] += [task]
    return dict_home_tasks


@dp.message_handler(text='Просмотреть дз')
async def main_view_hometasks(message: types.Message, edit=False):
    if not edit:
        await message.answer('Выберите, на которые дни отобразить ДЗ:',
                             reply_markup=inline_keyboards.view_hometasks())
    else:
        await message.edit_text('Выберите, на которые дни отобразить ДЗ:',
                             reply_markup=inline_keyboards.view_hometasks())


@dp.callback_query_handler(text='view_hometasks:today')
async def view_hometask_today(call: types.CallbackQuery):
    await call.answer()
    today = datetime.datetime.now()
    end_date = today + datetime.timedelta(days=1)

    list_home_tasks = await db.get_hometasks_date_interval(today, end_date)
    dict_home_tasks = {}
    if list_home_tasks:
        dict_home_tasks = get_dict_home_tasks(list_home_tasks)

    send_message = '<u>Домашние задания на сегодня:</u>\n'

    if dict_home_tasks:
        for day, tasks in dict_home_tasks.items():
            for task in tasks:
                send_message += f'\n<b>{task.lesson}:</b> {task.task}'
    else:
        send_message += '<i>Заданий нет.</i>'

    await call.message.edit_text(send_message, reply_markup=inline_keyboards.bf_view_task)


@dp.callback_query_handler(text='view_hometasks:tomorrow')
async def view_hometask_tomorrow(call: types.CallbackQuery):
    await call.answer()
    today = datetime.datetime.now() + datetime.timedelta(days=1)
    end_date = today + datetime.timedelta(days=1)

    list_home_tasks = await db.get_hometasks_date_interval(today, end_date)
    dict_home_tasks = {}
    if list_home_tasks:
        dict_home_tasks = get_dict_home_tasks(list_home_tasks)

    send_message = '<u>Домашние задания на завтра:</u>\n'

    if dict_home_tasks:
        for day, tasks in dict_home_tasks.items():
            for task in tasks:
                send_message += f'\n<b>{task.lesson}:</b> {task.task}'
    else:
        send_message += '<i>Заданий нет.</i>'

    await call.message.edit_text(send_message, reply_markup=inline_keyboards.bf_view_task)


@dp.callback_query_handler(text='view_hometasks:this_week')
async def view_hometask_this_week(call: types.CallbackQuery):
    await call.answer()
    this_day = datetime.datetime.now().isoweekday()

    if this_day != 1:
        today = datetime.datetime.now() - datetime.timedelta(days=this_day-1)
    else:
        today = datetime.datetime.now()
    end_date = today + datetime.timedelta(days=5)

    list_home_tasks = await db.get_hometasks_date_interval(today, end_date)
    dict_home_tasks = {}
    if list_home_tasks:
        dict_home_tasks = get_dict_home_tasks(list_home_tasks)

    send_message = '<u>Домашние задания на текущую неделю:</u>\n'

    list_keys = list(dict_home_tasks.keys())
    list_keys.sort()

    if dict_home_tasks:
        for day in list_keys:
            send_message += f'\n<b>{day}</b>:'
            for task in dict_home_tasks[day]:
                send_message += f'\n\t\t\t\t<b>{task.lesson}:</b> {task.task}'
    else:
        send_message += '<i>Заданий нет.</i>'

    await call.message.edit_text(send_message, reply_markup=inline_keyboards.bf_view_task)


@dp.callback_query_handler(text='view_hometasks:next_week')
async def view_hometask_next_week(call: types.CallbackQuery):
    await call.answer()
    this_day = datetime.datetime.now().isoweekday()

    if this_day != 1:
        today = datetime.datetime.now() - datetime.timedelta(days=this_day-1) + datetime.timedelta(days=7)
    else:
        today = datetime.datetime.now()
    end_date = today + datetime.timedelta(days=5)

    list_home_tasks = await db.get_hometasks_date_interval(today, end_date)
    dict_home_tasks = {}
    if list_home_tasks:
        dict_home_tasks = get_dict_home_tasks(list_home_tasks)

    send_message = '<u>Домашние задания на следующую неделю:</u>\n'

    list_keys = list(dict_home_tasks.keys())
    list_keys.sort()

    if dict_home_tasks:
        for day in list_keys:
            send_message += f'\n<b>{day}</b>:'
            for task in dict_home_tasks[day]:
                send_message += f'\n\t\t\t\t<b>{task.lesson}:</b> {task.task}'
    else:
        send_message += '<i>Заданий нет.</i>'

    await call.message.edit_text(send_message, reply_markup=inline_keyboards.bf_view_task)


@dp.callback_query_handler(text='view_hometasks:all_next')
async def view_hometask_next_week(call: types.CallbackQuery):
    await call.answer()
    this_day = datetime.datetime.now().isoweekday()

    today = datetime.datetime.now()
    end_date = today + datetime.timedelta(days=999999)

    list_home_tasks = await db.get_hometasks_date_interval(today, end_date)
    dict_home_tasks = {}
    if list_home_tasks:
        dict_home_tasks = get_dict_home_tasks(list_home_tasks)

    send_message = '<u>Домашние задания на следующую неделю:</u>\n'

    list_keys = list(dict_home_tasks.keys())
    list_keys.sort()

    if dict_home_tasks:
        for day in list_keys:
            send_message += f'\n<b>{day}</b>:'
            for task in dict_home_tasks[day]:
                send_message += f'\n\t\t\t\t<b>{task.lesson}:</b> {task.task}'
    else:
        send_message += '<i>Заданий нет.</i>'

    await call.message.edit_text(send_message, reply_markup=inline_keyboards.bf_view_task)


@dp.callback_query_handler(text='bf_view_task')
async def bf_view_task(call: types.CallbackQuery):
    await call.answer()
    await main_view_hometasks(call.message, edit=True)


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
        await message.answer('<i>Выберите предмет к которому хотите добавить дз:</i>',
                             reply_markup=await inline_keyboards.choice_subject())


@dp.callback_query_handler(text_startswith='choice_subject')
async def choice_data(call: types.CallbackQuery):
    subject = str(call.data).split(':')[1]
    await call.message.edit_text('<i>Выберите на которое число вы хотите добавить дз:</i>',
                                 reply_markup=await inline_keyboards.choice_date(subject))
    await HomeTasks.Task.set()


@dp.callback_query_handler(text_startswith='home_task', state=HomeTasks.Task)
async def message_enter_hometask(call: types.CallbackQuery, state: FSMContext, edit=False):
    await call.answer()
    if not edit:
        subject = str(call.data).split(':')[1]
        date = str(call.data).split(':')[2]
    else:
        state_data = await state.get_data()
        subject = state_data.get('subject')
        date = state_data.get('date')
    await state.update_data(subject=subject, date=date, from_call=True)

    await call.message.edit_text('Введите задание:',
                                 reply_markup=inline_keyboards.bf_enter_hometask(subject))


@dp.message_handler(state=HomeTasks.Task)
async def enter_hometask(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    subject = state_data.get('subject')
    from_call = state_data.get('from_call')
    if from_call:
        if message.text == 'Главное меню':
            await state.reset_state()
            await get_main_menu(message)
        elif message.text == 'Добавить':
            await state.reset_state()
            await choice_subject(message)
        elif message.text == 'Просмотреть дз':
            await state.reset_state()
            await message.answer('Смотрю дз)')
        else:
            date = state_data.get('date')
            date = str(date).split('-')
            year_date, month_date, day_date = date[0], date[1], date[2]
            list_date = [day_date, month_date, year_date]
            new_date = '.'.join(list_date)

            task = message.text
            await state.update_data(task=task)

            await message.answer(f'<i>{subject} - {new_date}</i>\n\n<b>Текст задания:</b> {task}\n\nВсё верно?',
                                 reply_markup=inline_keyboards.confirm_add_hometask())
    else:
        if message.text == 'Главное меню':
            await state.reset_state()
            await get_main_menu(message)
        elif message.text == 'Добавить':
            await state.reset_state()
            await choice_subject(message)
        elif message.text == 'Просмотреть дз':
            await state.reset_state()
            await message.answer('Смотрю дз)')
        else:
            pass


@dp.callback_query_handler(text='add_home_task:true', state=HomeTasks.Task)
async def confirm_add_hometask(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    state_data = await state.get_data()
    subject = state_data.get('subject')
    task = state_data.get('task')

    date = state_data.get('date')
    date = date.split('-')
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])

    user_class_id = await db.get_id_class()

    task_model = db.home_task()
    task_model.class_id = int(user_class_id)
    task_model.lesson = subject
    task_model.task = task

    task_model.date = datetime.date(year, month, day)

    await task_model.create()

    await call.message.edit_text('Задание успешно добавлено!')
    await state.reset_state()


@dp.callback_query_handler(text='add_home_task:false', state=HomeTasks.Task)
async def confirm_add_hometask(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await message_enter_hometask(call, state, edit=True)


@dp.callback_query_handler(text_startswith='bf_enter_hometask', state=HomeTasks.Task)
async def bf_enter_hometask(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await choice_data(call)


@dp.callback_query_handler(text='bf_choice_date', state=HomeTasks.Task)
async def bf_choice_date(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await state.reset_state()
    await choice_subject(call.message)
