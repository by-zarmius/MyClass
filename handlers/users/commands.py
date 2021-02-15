from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, CommandHelp
from aiogram.utils.deep_linking import decode_payload

from utils.db_api import db_commands

from loader import dp

from templates import commands
from keyboards.default import main_keyboard


db = db_commands


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    try:
        encode_join_code = message.text.split(' ')[1]
        join_code = decode_payload(encode_join_code)
        class_id = join_code.split('_')[1]
        user_id = types.User.get_current().id

        other_class = await db.get_class()
        if not other_class:
            user_class = await db.get_class_by_id(class_id)
            user_class.members += [user_id]
            await user_class.update(members=user_class.members).apply()
            await message.answer(f'Вы присоединились к классу: {user_class.name}')
            await get_main_menu(message)
        else:
            await message.answer(f'Вы уже являетесь участником класса: {other_class.name}')
    except IndexError:
        pass
    create_user = await db.new_user()

    if create_user['create']:
        await message.answer(commands.start_message.format(types.User.get_current().full_name))
        await message.answer(commands.create_class, reply_markup=main_keyboard.start_menu_for_new_user)
    else:
        user_class = await db.check_in_class()
        if user_class:
            await message.answer(commands.start_message.format(types.User.get_current().full_name),
                                 reply_markup=main_keyboard.main_menu)
        else:
            await message.answer(commands.start_message.format(types.User.get_current().full_name),
                                 reply_markup=main_keyboard.start_menu_for_new_user)


@dp.message_handler(commands=['detail'])
async def detail_bot(message: types.Message):
    await message.answer(commands.detail)


@dp.message_handler(commands=['menu'])
async def get_main_menu(message: types.Message):
    user_class = await db.check_in_class()
    if user_class:
        await message.answer('<i>Главное меню:</i>', reply_markup=main_keyboard.main_menu, parse_mode='html')
    else:
        await message.answer('<i>Главное меню:</i>',
                             reply_markup=main_keyboard.start_menu_for_new_user,
                             parse_mode='html')


@dp.message_handler(commands=['commands'])
async def get_commands(message: types.Message):
    text = ("Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку",
            "/menu - Получить главное меню, если оно исчезло",
            "/detail - Более детальная информация о боте",
            "/commands - Получить список всех команд и их краткое описание")

    await message.answer("\n".join(text))

@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("Выберите, что хотите узнать: ",
            "/how_create_class - Создание класса",
            "/how_join_class - Как присоедениться к существующему классу",
            "/how_add_schedule - Как добавить расписание класса",
            "/how_add_home_task - Как добавить ДЗ",
            "Позже будут добавлены разделы помощи ещё по нескольким пунктам!)",)

    await message.answer("\n".join(text))

@dp.message_handler(commands=['how_create_class'])
async def how_create_class(message: types.Message):
    send_message = '<b>Как создать новый класс</b>\n\n'
    send_message += 'Чтобы создать новый класс(вы это можете сделать только если не являетесь участником класса), вам нужно перейти в раздел "Мой класс", нажать кнопку "Создать класс", после чего следуйте инстукциями'
    await message.answer(send_message)


@dp.message_handler(commands=['how_join_class'])
async def how_create_class(message: types.Message):
    send_message = '<b>Как присоедениться к существующему классу</b>\n\n'
    send_message += 'Стать участником сущетсвующего класса вы можете двумя способами. \n\nПервый заключается в том, чтобы узнать у других участников код класса, который вы можете ввести в "Мой класс" -> "Присоедениться" \n\nВторой способ заключается в том, чтобы другой участник класса отправил вам пригласительную ссылку на него. Вам всего лишь останется на неё нажать.'
    await message.answer(send_message)


@dp.message_handler(commands=['how_add_schedule'])
async def how_create_class(message: types.Message):
    send_message = '<b>Как добавить расписание класса</b>\n\n'
    send_message += 'Чтобы добавить расписание класса вам нужно перейти в раздел "Распорядок" и нажать на пункт "Изменить", выбрать нужный день и начать писать уроки по порядку. В конце нажать на кнопку "Закончить"'
    await message.answer(send_message)


@dp.message_handler(commands=['how_add_home_task'])
async def how_create_class(message: types.Message):
    send_message = '<b>Как добавить ДЗ</b>\n\n'
    send_message += 'Для этого вам нужно перейти в раздел "ДЗ", пункт "Добавить", выбрать предмет по которому вы хотите добавить ДЗ, выбрать на который день вы хотите его добавить и в конце концов просто его записать и подтверить.\n\n<u><b>ВАЖНО!</b> Все предметы подтягиваются из расписания уроков. Если какого-то предмета в списке нет, значит вы не добавили его в своё расписание уроков!</u>'
    await message.answer(send_message)
