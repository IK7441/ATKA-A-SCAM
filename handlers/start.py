from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database import register_user
from keyboards.menu import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    await register_user(message.from_user)

    await message.answer(
        "🛡️ <b>ATKA A-Scam</b>\n\n"
        "Добро пожаловать в систему "
        "проверки мошенников!\n\n"
        "🔍 Проверяйте подозрительных пользователей.\n"
        "🚨 Сообщайте о мошенничестве.\n"
        "🛡️ Помогайте защищать других.\n\n"
        "Выберите действие:",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )