from aiogram import types
from aiogram.dispatcher import FSMContext

from utils.db_api import db_commands
from gino import Gino

from loader import dp

from keyboards.default import main_keyboard
from keyboards.inline import inline_keyboards
from states.all_states import NewSchedule

from .commands import get_main_menu


db = db_commands


async def create_schedule_of_day(day):
    schedule = await db.get_schedule()

    schedule_week_dict = {
        'Понедельник': schedule.monday,
        'Вторник': schedule.tuesday,
        'Среда': schedule.wednesday,
        'Четверг': schedule.thursday,
        'Пятница': schedule.friday
    }

    send_message = f'<u>Распорядок дня: <b>{day}</b>:</u>'
    list_lessons = schedule_week_dict[day]
    if list_lessons:
        lessons = ''
        counter = 1
        for lesson in list_lessons:
            lessons += f'\n{counter}) {lesson}'
            counter += 1
        send_message += f'{lessons}'
    else:
        send_message += 'Пусто...'

    return send_message


@dp.message_handler(text='Распорядок')
async def main_schedule(message: types.Message):
    user_have_class = await db.check_in_class()
    if not user_have_class:
        await message.answer('Это доступно только пользователям, которые являются участником класса')
    else:
        user = await db.get_user()
        full_name_user = types.User.get_current().full_name
        await user.update(tg_nickname=full_name_user).apply()

        await message.answer('Выберите действие:', reply_markup=main_keyboard.lesson_schedule)


@dp.message_handler(text='Просмотреть распорядок')
async def choice_day_watch_schedule(message: types.Message, edit=False):
    user_have_class = await db.check_in_class()
    if not user_have_class:
        await message.answer('Это доступно только пользователям, которые являются участником класса')
    else:
        if not edit:
            await message.answer('Расписание на который день отобразить:',
                                 reply_markup=inline_keyboards.watch_schedule_days)
        else:
            await message.edit_text('Расписание на который день отобразить:',
                                 reply_markup=inline_keyboards.watch_schedule_days)

@dp.callback_query_handler(text_startswith='watch_schedule_days')
async def watch_schedule(call: types.CallbackQuery):
    await call.answer()
    day = str(call.data).split(':')[1]

    schedule = await db.get_schedule()

    schedule_week_dict = {
        'Понедельник': schedule.monday,
        'Вторник': schedule.tuesday,
        'Среда': schedule.wednesday,
        'Четверг': schedule.thursday,
        'Пятница': schedule.friday
    }

    if day == 'week':
        send_message = '<u>Распорядок на неделю:</u>'
        for day, data in schedule_week_dict.items():
            if schedule_week_dict[day]:
                lessons = ''
                counter = 1
                for lesson in data:
                    lessons += f'\n{counter}) {lesson}'
                    counter += 1

                send_message += f'\n\n<b>{day}</b>:{lessons}'
            else:
                send_message += f'\n\n<b>{day}:</b> Пусто...'
    elif day == 'monday':
        send_message = await create_schedule_of_day('Понедельник')
    elif day == 'tuesday':
        send_message = await create_schedule_of_day('Вторник')
    elif day == 'wednesday':
        send_message = await create_schedule_of_day('Среда')
    elif day == 'thursday':
        send_message = await create_schedule_of_day('Четверг')
    elif day == 'friday':
        send_message = await create_schedule_of_day('Пятница')

    await call.message.edit_text(send_message, reply_markup=inline_keyboards.from_schedule, parse_mode='html')


@dp.callback_query_handler(text='back_to_main_schedule')
async def back_to_main_schedule(call: types.CallbackQuery):
    await call.answer()
    await choice_day_watch_schedule(call.message, edit=True)


@dp.message_handler(text='Изменить')
async def edit_schedule(message: types.Message):
    user_have_class = await db.check_in_class()
    if not user_have_class:
        await message.answer('Это доступно только пользователям, которые являются участником класса')
    else:
        send_message = '<u>Распорядок на неделю:</u>'
        schedule = await db.get_schedule()
        monday = schedule.monday
        tuesday = schedule.tuesday
        wednesday = schedule.wednesday
        thursday = schedule.thursday
        friday = schedule.friday

        schedule_week_dict = {
            'Понедельник': monday,
            'Вторник': tuesday,
            'Среда': wednesday,
            'Четверг': thursday,
            'Пятница': friday
        }

        for day, data in schedule_week_dict.items():
            if schedule_week_dict[day]:
                lessons = ''
                counter = 1
                for lesson in data:
                    lessons += f'\n{counter}) {lesson}'
                    counter += 1

                send_message += f'\n\n<b>{day}</b>:{lessons}'
            else:
                send_message += f'\n\n<b>{day}:</b> Пусто...'

        send_message += '\n\n<i>Выберите, расписаник которого дня вы хотите изменить:</i>'

        await message.answer(send_message, reply_markup=inline_keyboards.schedule_days, parse_mode='html')
        await NewSchedule.Schedule.set()


@dp.callback_query_handler(text_startswith='schedule_days:', state=NewSchedule.Schedule)
async def enter_schedule(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    day = str(call.data).split(':')[1]
    await state.update_data(day=day)
    await call.message.edit_text('А теперь отправляйте мне каждый предмет по порядку'
                                 '\n\n<i>(<b>Внимание!</b> Смотрите, чтобы предмет был написан в одном '
                                 'и том же стиле(Чтобы не было: "Русский" и "Русский язык"))</i>')


@dp.message_handler(state=NewSchedule.Schedule)
async def add_new_lesson(message: types.Message, state: FSMContext):
    if message.text == 'Главное меню':
        await state.reset_state()
        await get_main_menu(message)
    elif message.text == 'Просмотреть распорядок':
        await state.reset_state()
        await choice_day_watch_schedule(message)
    else:
        state_data = await state.get_data()
        day = state_data.get('day')
        if day:
            schedule = state_data.get('schedule')

            if not schedule:
                schedule = []
            schedule.append(message.text)
            await state.update_data(schedule=schedule)

            send_message = 'Вы добавили:'
            counter = 1
            for lesson in schedule:
                send_message += f'\n{counter}) {lesson}'
                counter += 1

            await message.answer(send_message, reply_markup=inline_keyboards.schedule_end_edit)


@dp.callback_query_handler(text='end_edit_schedule', state=NewSchedule.Schedule)
async def end_edit_schedule(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    state_data = await state.get_data()
    day = state_data.get('day')
    schedule = state_data.get('schedule')

    lesson_schedule = await db.get_schedule()

    if day == 'monday':
        await lesson_schedule.update(monday=schedule).apply()
    elif day == 'tuesday':
        await lesson_schedule.update(tuesday=schedule).apply()
    elif day == 'wednesday':
        await lesson_schedule.update(wednesday=schedule).apply()
    elif day == 'thursday':
        await lesson_schedule.update(thursday=schedule).apply()
    elif day == 'friday':
        await lesson_schedule.update(friday=schedule).apply()

    await state.reset_state()

    await edit_schedule(call.message)
