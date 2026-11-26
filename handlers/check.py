from aiogram import Router, F
from aiogram.types import Message

from database import check_user

router = Router()


def detect_type(value):

    value = value.strip()

    if value.startswith("@"):
        return "username", value.lower()

    if value.isdigit():
        return "telegram_id", value

    if "@" in value and "." in value:
        return "email", value.lower()

    if value.startswith("+"):
        return "phone", value

    return None, None


@router.message(F.text == "🔍 Проверить пользователя")
async def check_start(message: Message):

    await message.answer(
        "🔍 <b>Проверка пользователя</b>\n\n"
        "Отправь мне один из идентификаторов:\n\n"
        "• Telegram username\n"
        "• Telegram ID\n"
        "• Номер телефона\n"
        "• Электронную почту",
        parse_mode="HTML"
    )


@router.message(F.text)
async def check_identifier(message: Message):

    value = message.text.strip()

    if value.startswith("/"):
        return

    identifier_type, identifier = detect_type(value)

    if not identifier_type:
        return

    result = await check_user(
        identifier_type,
        identifier
    )

    if result:

        scammer = result[0]

        await message.answer(
            "🔴 <b>ОБНАРУЖЕН В БАЗЕ!</b>\n\n"
            f"Идентификатор: <code>{identifier}</code>\n"
            f"Тип: {scammer['scam_type']}\n"
            f"Жалоб: {scammer['report_count']}\n\n"
            f"Описание:\n{scammer['description']}\n\n"
            "⚠️ Будьте осторожны!",
            parse_mode="HTML"
        )

    else:

        await message.answer(
            "🟢 <b>ВНУТРЕННЯЯ БАЗА</b>\n\n"
            f"Идентификатор: <code>{identifier}</code>\n\n"
            "Совпадений не обнаружено.\n\n"
            "Это не гарантирует безопасность "
            "пользователя.",
            parse_mode="HTML"
        )