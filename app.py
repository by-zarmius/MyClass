from aiogram import executor

from loader import dp
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.db_api.db_commands import create_db


async def on_startup(dispatcher):
    # Уведомляет про запуск
    await create_db()
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
