from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from utils.db_api import db_commands

db = db_commands.DBCommands()

create_class_cd = CallbackData('create_class', 'action')
notice_cd = CallbackData('notice', 'action')
delete_notice_cd = CallbackData('delete_notice', 'notice')

events_cd = CallbackData('events', 'action')
event_create_task_cd = CallbackData('event_create_tasks', 'action')
list_events_cd = CallbackData('list_events', 'action', 'event')
check_delete_event_cd = CallbackData('check_remove_event', 'action', 'id')

main_task_cd = CallbackData('main_task', 'action', 'id')

schedule_days_cd = CallbackData('schedule_days', 'day')
watch_schedule_days_cd = CallbackData('watch_schedule_days', 'day')

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


async def list_events(action):
    events = await db.get_event()
    kb = types.InlineKeyboardMarkup()

    for event in events:
        kb.add(types.InlineKeyboardButton(event.name, callback_data=list_events_cd.new(action=action, event=str(event.id))))
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

