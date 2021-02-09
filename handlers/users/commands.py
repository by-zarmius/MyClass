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


@dp.message_handler(commands=['add_member'])
async def add_member(message: types.Message):
    await message.answer('<i>Чтобы добавить нового участника в класс, скиньте ему код вашего класса, который он может ввести в разделе: Мой класс -> Добавить класс(Конечно же, если он ещё не состоит в каком-либо классе). Или же просто отправьте ему ссылку, при нажатии на которую его переадресует к вашему классу - t.me/...</i>')

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
