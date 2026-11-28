import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, validate_config

from handlers import start, check, report, admin


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


async def main():

    validate_config()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp = Dispatcher(
        storage=MemoryStorage()
    )

    dp.include_router(start.router)
    dp.include_router(report.router)
    dp.include_router(check.router)
    dp.include_router(admin.router)

    await bot.set_my_commands([
        BotCommand(
            command="start",
            description="Главное меню"
        ),
        BotCommand(
            command="check",
            description="Проверить пользователя"
        ),
        BotCommand(
            command="report",
            description="Сообщить о мошеннике"
        ),
        BotCommand(
            command="stats",
            description="Статистика"
        ),
        BotCommand(
            command="admin",
            description="Админ-панель"
        ),
        BotCommand(
            command="cancel",
            description="Отменить действие"
        )
    ])

    logging.info("ATKA A-Scam запущен!")

    try:
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())