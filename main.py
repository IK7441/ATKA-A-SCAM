import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN

from handlers import start
from handlers import check
from handlers import report
from handlers import admin


async def main():

    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=BOT_TOKEN)

    dp = Dispatcher(
        storage=MemoryStorage()
    )

    dp.include_router(start.router)
    dp.include_router(check.router)
    dp.include_router(report.router)
    dp.include_router(admin.router)

    print("ATKA A-Scam started!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())