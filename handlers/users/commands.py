from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, CommandHelp

from utils.db_api import db_commands

from loader import dp

from templates import commands
from keyboards.default import main_keyboard


db = db_commands.DBCommands()


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    create_user = await db.new_user()
    await message.answer(commands.start_message.format(types.User.get_current().full_name))

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


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку")

    await message.answer("\n".join(text))


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

# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
# @dp.message_handler(state=None)
# async def bot_echo(message: types.Message):
#     await message.answer(f"Эхо без состояния."
#                          f"Сообщение:\n"
#                          f"{message.text}")
#
#
# # Эхо хендлер, куда летят ВСЕ сообщения с указанным состоянием
# @dp.message_handler(state="*", content_types=types.ContentTypes.ANY)
# async def bot_echo_all(message: types.Message, state: FSMContext):
#     state = await state.get_state()
#     await message.answer(f"Эхо в состоянии <code>{state}</code>.\n"
#                          f"\nСодержание сообщения:\n"
#                          f"<code>{message}</code>")
