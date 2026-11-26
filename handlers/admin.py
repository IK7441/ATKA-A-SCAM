from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from config import ADMIN_IDS
from database import get_statistics, get_latest

router = Router()


@router.message(F.text == "/admin")
async def admin_panel(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    stats = await get_statistics()

    await message.answer(
        "👮 <b>ATKA ADMIN PANEL</b>\n\n"
        f"Скамеров: {stats['scammers']}\n"
        f"Жалоб: {stats['reports']}\n"
        f"На проверке: {stats['pending']}",
        parse_mode="HTML"
    )


@router.message(F.text == "📊 Статистика")
async def statistics(message: Message):

    stats = await get_statistics()

    await message.answer(
        "📊 <b>ATKA A-Scam Statistics</b>\n\n"
        f"🔴 Записей в базе: {stats['scammers']}\n"
        f"📨 Всего жалоб: {stats['reports']}\n"
        f"🟡 На проверке: {stats['pending']}",
        parse_mode="HTML"
    )


@router.message(F.text == "🆕 Последние скамеры")
async def latest(message: Message):

    scammers = await get_latest()

    if not scammers:
        await message.answer("Пока база пуста.")
        return

    text = "🆕 <b>Последние записи</b>\n\n"

    for scammer in scammers:
        text += (
            f"🔴 {scammer['identifier_value']}\n"
            f"Тип: {scammer['scam_type']}\n\n"
        )

    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "ℹ️ О проекте")
async def about(message: Message):

    await message.answer(
        "🛡️ <b>ATKA A-Scam</b>\n\n"
        "Независимый проект по борьбе "
        "с мошенничеством в Telegram.\n\n"
        "Проверяй. Сообщай. Защищай.\n\n"
        "ATKA ANTI SCAM",
        parse_mode="HTML"
    )