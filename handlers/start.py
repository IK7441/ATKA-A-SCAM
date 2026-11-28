from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import register_user
from keyboards.menu import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    await register_user(message.from_user)

    await message.answer(
        "🛡 <b>ATKA A-Scam</b>\n\n"
        "Добро пожаловать!\n\n"
        "Здесь можно проверить пользователя "
        "или сообщить о мошенничестве.\n\n"
        "⚠️ Отсутствие записи в базе не гарантирует безопасность.",
        reply_markup=main_menu()
    )


@router.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Действие отменено.",
        reply_markup=main_menu()
    )


@router.message(F.text == "ℹ️ О проекте")
async def about(message: Message):
    await message.answer(
        "<b>ATKA A-Scam</b>\n\n"
        "Проект предназначен для проверки подозрительных "
        "идентификаторов и сбора жалоб.\n\n"
        "Каждая жалоба проходит модерацию. "
        "Без одобрения администратора запись не попадёт "
        "в основную базу."
    )