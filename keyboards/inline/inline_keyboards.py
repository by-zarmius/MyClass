from datetime import datetime, timedelta
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from utils.db_api import db_commands

db = db_commands

create_class_cd = CallbackData('create_class', 'action')
notice_cd = CallbackData('notice', 'action')
delete_notice_cd = CallbackData('delete_notice', 'notice')

events_cd = CallbackData('events', 'action')
event_create_task_cd = CallbackData('event_create_tasks', 'action')
list_events_cd = CallbackData('list_events', 'action', 'event')
check_delete_event_cd = CallbackData('check_remove_event', 'action', 'id')
main_task_cd = CallbackData('main_task', 'action', 'id')
delete_task_cd = CallbackData('delete_task', 'task_id', 'event_id')
choice_complete_tasks_cd = CallbackData('cc_tasks', 'task_id', 'event_id', 'status')

edit_event_cd = CallbackData('edit_event', 'action', 'event_id')

schedule_days_cd = CallbackData('schedule_days', 'day')
watch_schedule_days_cd = CallbackData('watch_schedule_days', 'day')

choice_subject_cd = CallbackData('choice_subject', 'subject')

my_class_cd = CallbackData('my_class', 'action')
view_hometasks_cd = CallbackData('view_hometasks', 'date')

create_class = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Да!', callback_data=create_class_cd.new(action='confirm')),
            InlineKeyboardButton(text='Вести заново', callback_data=create_class_cd.new(action='repeat')),
        ]
    ]
)

notice_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Добавить объявление', callback_data=notice_cd.new(action='add'))],
        [InlineKeyboardButton(text='Удалить объявление', callback_data=notice_cd.new(action='remove'))],
    ]
)

no_notice_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Добавить объявление', callback_data=notice_cd.new(action='add'))],
    ]
)


async def delete_notice():
    notices = await db.get_notice()
    kb = types.InlineKeyboardMarkup()

    for notice in notices:
        kb.add(types.InlineKeyboardButton(notice.name, callback_data=delete_notice_cd.new(notice=str(notice.id))))
    kb.add(types.InlineKeyboardButton('Назад', callback_data='back_from_notice'))

    return kb


events_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Добавить мероприятие', callback_data=events_cd.new(action='add'))],
        [
            InlineKeyboardButton(text='Изменить', callback_data=events_cd.new(action='edit')),
            InlineKeyboardButton(text='Удалить', callback_data=events_cd.new(action='remove'))
        ],
        [InlineKeyboardButton(text='Задания', callback_data=events_cd.new(action='tasks'))],
    ]
)

no_events_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Добавить мероприятие', callback_data=events_cd.new(action='add'))],
    ]
)

event_create_task = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Да', callback_data=event_create_task_cd.new(action='yes')),
            InlineKeyboardButton(text='Нет', callback_data=event_create_task_cd.new(action='no'))
        ]
    ]
)

event_add_more_task = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Закончить', callback_data='end_enter_task_for_event')
        ]
    ]
)

event_end_enter_tasks = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Закончить',
                                                                        callback_data='to_event_detail'))


async def list_events(action):
    events = await db.get_event()
    kb = types.InlineKeyboardMarkup()

    for event in events:
        kb.add(types.InlineKeyboardButton(event.name,
                                          callback_data=list_events_cd.new(action=action, event=str(event.id))))
    kb.add(types.InlineKeyboardButton('Назад', callback_data='back_from_event'))

    return kb


async def check_delete_event(id):
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Да', callback_data=check_delete_event_cd.new(action='yes', id=id)),
                InlineKeyboardButton(text='Нет', callback_data=check_delete_event_cd.new(action='no', id=id)),
            ]
        ]
    )


async def main_task(id):
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить', callback_data=main_task_cd.new(action='add', id=id)),
                InlineKeyboardButton(text='Удалить', callback_data=main_task_cd.new(action='delete', id=id)),
            ],
            [
                InlineKeyboardButton(text='Выбрать выполненное задание',
                                     callback_data=main_task_cd.new(action='choice_complete', id=id))
            ],
            [
                InlineKeyboardButton(text='Назад', callback_data='back_from_task')
            ]
        ]
    )


async def choose_task_delete(event_id):
    kb = InlineKeyboardMarkup()
    event = await db.get_event_by_id(event_id)
    counter = 0
    for task in event.tasks:
        kb.add(InlineKeyboardButton(text=task, callback_data=delete_task_cd.new(event_id=event_id, task_id=counter)))
        counter += 1
    kb.add(InlineKeyboardButton(text='Вернуться', callback_data=f'back_from_delete_task:{event_id}'))
    return kb


async def choice_complete_tasks(event_id):
    kb = InlineKeyboardMarkup()
    event = await db.get_event_by_id(event_id)
    if not event.complete_tasks:
        event.complete_tasks = []
    if not event.tasks:
        event.tasks = []

    complete_counter = 0
    for complete_task in event.complete_tasks:
        kb.add(InlineKeyboardButton(text='✅' + complete_task,
                                    callback_data=choice_complete_tasks_cd.new(
                                        event_id=event_id,
                                        task_id=complete_counter,
                                        status='complete'
                                    )))
    task_counter = 0
    for task in event.tasks:
        kb.add(InlineKeyboardButton(text=task,
                                    callback_data=choice_complete_tasks_cd.new(
                                        event_id=event_id,
                                        task_id=task_counter,
                                        status='work'
                                    )))
    kb.add(InlineKeyboardButton(text='Готово\Вернуться', callback_data=f'bf_choice_complete_task:{event_id}'))
    return kb


def edit_event(event_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Название', callback_data=edit_event_cd.new(event_id=event_id, action='name'))),
    kb.add(InlineKeyboardButton(text='Описание',
                                callback_data=edit_event_cd.new(event_id=event_id, action='description'))),
    kb.add(InlineKeyboardButton(text='Дата', callback_data=edit_event_cd.new(event_id=event_id, action='date'))),
    kb.add(InlineKeyboardButton(text='Вернуться', callback_data='bf_edit_event'))
    return kb


def to_main_edit_event(event_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Вернуться', callback_data=f'to_main_edit_event:{event_id}'))
    return kb


schedule_days = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Понедельник', callback_data=schedule_days_cd.new(day='monday')),
            InlineKeyboardButton(text='Вторник', callback_data=schedule_days_cd.new(day='tuesday'))
        ],
        [
            InlineKeyboardButton(text='Среда', callback_data=schedule_days_cd.new(day='wednesday')),
            InlineKeyboardButton(text='Четверг', callback_data=schedule_days_cd.new(day='thursday'))
        ],
        [InlineKeyboardButton(text='Пятница', callback_data=schedule_days_cd.new(day='friday'))],
    ]
)

watch_schedule_days = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Неделя', callback_data=watch_schedule_days_cd.new(day='week'))
        ],
        [
            InlineKeyboardButton(text='Понедельник', callback_data=watch_schedule_days_cd.new(day='monday')),
            InlineKeyboardButton(text='Вторник', callback_data=watch_schedule_days_cd.new(day='tuesday'))
        ],
        [
            InlineKeyboardButton(text='Среда', callback_data=watch_schedule_days_cd.new(day='wednesday')),
            InlineKeyboardButton(text='Четверг', callback_data=watch_schedule_days_cd.new(day='thursday')),
        ],
        [
            InlineKeyboardButton(text='Пятница', callback_data=watch_schedule_days_cd.new(day='friday'))
        ]
    ]
)

schedule_end_edit = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Закончить', callback_data='end_edit_schedule')]
    ]
)

from_schedule = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='back_to_main_schedule')]
    ]
)


async def choice_subject():
    kb = InlineKeyboardMarkup()

    subjects = list(await db.get_set_all_subjects())
    subjects.sort()
    subjects.reverse()
    subjects_list_2 = []
    temp_list = []
    for i in range(0, len(subjects)):
        lesson = subjects.pop()
        temp_list.append(lesson)

        if len(temp_list) == 2:
            subjects_list_2.append(temp_list)
            temp_list = []

    for subject in subjects_list_2:
        if len(subject) == 2:
            kb.row(
                InlineKeyboardButton(text=subject[0], callback_data=choice_subject_cd.new(subject=subject[0])),
                InlineKeyboardButton(text=subject[1], callback_data=choice_subject_cd.new(subject=subject[1]))
            )
        else:
            kb.row(
                InlineKeyboardButton(text=subject[0], callback_data=choice_subject_cd.new(subject=subject[0]))
            )
    return kb


def edit_class():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Изменить',
                                callback_data=my_class_cd.new(action='edit')))
    kb.add(InlineKeyboardButton(text='Участники класса',
                                callback_data=my_class_cd.new(action='view_members')))
    return kb


to_my_class = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text='Вернуться', callback_data='to_my_class')
)


def edit_info_class():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Название', callback_data='edit_class:name'))
    kb.add(InlineKeyboardButton(text='Прикреплённый чат', callback_data='edit_class:tg_chat'))
    return kb


def edit_user_name():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Изменить имя', callback_data='user:edit_name'))
    return kb


def exit_from_class():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text='Да.', callback_data='exit_from_class:yes'))
    kb.add(InlineKeyboardButton(text='Нет!', callback_data='exit_from_class:no'))
    return kb


async def choice_date(subject):
    kb = InlineKeyboardMarkup()
    day_of_week = int(datetime.now().isoweekday())
    days_lesson = await db.get_days_of_subject(subject)

    full_days_lesson = []

    while len(full_days_lesson) < 20:
        full_days_lesson += days_lesson

    full_days_lesson = full_days_lesson[:20]
    full_days_lesson = list(map(lambda x: int(x), full_days_lesson))

    week = {
        1: 'Понедельник',
        2: 'Вторник',
        3: 'Среда',
        4: 'Четверг',
        5: 'Пятница',
        6: 'Суббота',
        7: 'Воскресенье',
    }

    date_lessons = []
    format_date_lessons = []
    last_day = 0
    days_passed = 0
    for day in full_days_lesson:
        if last_day < day:
            last_day = day
        else:
            days_passed += 7
            last_day = day

        if day > day_of_week:
            days_next_lesson = (day - day_of_week) + days_passed
        elif day == day_of_week:
            if days_passed != 0:
                days_next_lesson = days_passed
            else:
                continue
        elif day < day_of_week:
            if days_passed != 0:
                days_next_lesson = days_passed - (day_of_week - day)
            else:
                continue

        date_next_lesson = datetime.now().date() + timedelta(days=days_next_lesson)
        date_lessons.append(date_next_lesson)

        date = str(date_next_lesson).split('-')
        year_date, month_date, day_date = date[0], date[1], date[2]
        list_date = [day_date, month_date, year_date]
        new_date = f'{week[day]} - ' + '.'.join(list_date)

        format_date_lessons.append(new_date)

    format_date_lessons = format_date_lessons[:4]

    counter = 0
    for date_lesson in format_date_lessons:
        kb.add(
            InlineKeyboardButton(
                date_lesson,
                callback_data=f'home_task:{subject}:{date_lessons[counter]}'
            )
        )
        counter += 1
    kb.add(InlineKeyboardButton(text='Ввести другую дату',
                                callback_data=f'enter_other_date:{subject}'))
    kb.add(InlineKeyboardButton(text='Вернуться', callback_data='bf_choice_date'))

    return kb


def bf_enter_hometask(subject):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        text='Вернуться', callback_data=f'bf_enter_hometask:{subject}'
    ))
    return kb


def confirm_add_hometask():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        text='Да!', callback_data='add_home_task:true'
    ))
    kb.add(InlineKeyboardButton(
        text='Ввести заново...', callback_data='add_home_task:false'
    ))

    return kb


def view_hometasks():
    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton(text='На сегодня',
                             callback_data=view_hometasks_cd.new(
                                 date='today')
                             ),
        InlineKeyboardButton(text='На завтра',
                             callback_data=view_hometasks_cd.new(
                                 date='tomorrow')
                             )
    )
    kb.row(
        InlineKeyboardButton(text='Текущая неделя',
                             callback_data=view_hometasks_cd.new(
                                 date='this_week')
                             ),
        InlineKeyboardButton(text='Следующая неделя',
                             callback_data=view_hometasks_cd.new(
                                 date='next_week')
                             ),
    )

    kb.add(
        InlineKeyboardButton(text='Все следующие',
                             callback_data=view_hometasks_cd.new(
                                 date='all_next'
                             ))
    )
    return kb


bf_view_task = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Вернуться', callback_data='bf_view_task')]
    ]
)


















