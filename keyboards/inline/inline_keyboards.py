from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from utils.db_api import db_commands

db = db_commands.DBCommands()

create_class_cd = CallbackData('create_class', 'action')
notice_cd = CallbackData('notice', 'action')
delete_notice_cd = CallbackData('delete_notice', 'notice')

events_cd = CallbackData('events', 'action')

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
        [InlineKeyboardButton(text='Добавить объявление', callback_data=events_cd.new(action='add'))],
        [InlineKeyboardButton(text='Изменить объявление', callback_data=events_cd.new(action='edit'))],
        [InlineKeyboardButton(text='Удалить объявление', callback_data=events_cd.new(action='remove'))],
    ]
)

no_events_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Добавить объявление', callback_data=events_cd.new(action='add'))],
    ]
)
