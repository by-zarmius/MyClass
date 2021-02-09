from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_menu_for_new_user = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Мой класс'),
            KeyboardButton(text='Настройки'),
        ],
    ],
    resize_keyboard=True
)

without_class = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Создать класс'),
            KeyboardButton(text='Присоединиться'),
        ],
        [
            KeyboardButton(text='Главное меню'),
        ]
    ]
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Распорядок'),
            KeyboardButton(text='Мой класс'),
            KeyboardButton(text='ДЗ'),
        ],
        [
            KeyboardButton(text='Жизнь класса'),
        ],
        [
            KeyboardButton(text='Настройки'),
        ]
    ]
)

class_life = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Мероприятия'),
            KeyboardButton(text='Объявления'),
        ],
        [
            KeyboardButton(text='Главное меню'),
        ],
    ]
)

home_tasks_main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Просмотреть дз'),
            KeyboardButton(text='Добавить')
        ],
        [
            KeyboardButton(text='Главное меню'),
        ]
    ]
)

lesson_schedule = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Просмотреть распорядок'),
            KeyboardButton(text='Изменить'),
        ],
        [
            KeyboardButton(text='Главное меню'),
        ]
    ]
)

settings_buttons = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Изменить имя'),
            KeyboardButton(text='Выйти из класса')
        ],
        [
            KeyboardButton(text='Главное меню')
        ]
    ]
)
