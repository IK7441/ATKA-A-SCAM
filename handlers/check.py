import re
from html import escape

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import check_user
from keyboards.menu import main_menu

router = Router()


class CheckForm(StatesGroup):
    identifier = State()


def detect_type(raw):
    value = (raw or "").strip()

    if not value or len(value) > 320:
        return None, None

    if re.fullmatch(r"@[A-Za-z0-9_]{5,32}", value):
        return "username", value.lower()

    if re.fullmatch(r"[0-9]{5,20}", value):
        return "telegram_id", value

    if re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
        return "email", value.lower()

    if (
        re.fullmatch(r"\+?[0-9()\-\s]{7,24}", value)
        and any(c.isdigit() for c in value)
    ):
        phone = re.sub(r"[()\-\s]", "", value)
        return "phone", phone

    return None, None


async def start_check(message, state):
    await state.set_state(CheckForm.identifier)

    await message.answer(
        "🔍 <b>Проверка пользователя</b>\n\n"
        "Отправь один из вариантов:\n"
        "• @username\n"
        "• Telegram ID\n"
        "• Номер телефона\n"
        "• Email\n\n"
        "Для отмены напиши /cancel."
    )


@router.message(Command("check"))
async def check_command(message: Message, state: FSMContext):
    await start_check(message, state)


@router.message(F.text == "🔍 Проверить пользователя")
async def check_button(message: Message, state: FSMContext):
    await start_check(message, state)


@router.message(CheckForm.identifier)
async def check_identifier(message: Message, state: FSMContext):

    if not message.text:
        await message.answer(
            "Отправь текстовый идентификатор."
        )
        return

    kind, value = detect_type(message.text)

    if not kind:
        await message.answer(
            "❌ Неверный формат.\n\n"
            "Примеры:\n"
            "@username\n"
            "123456789\n"
            "+49123456789\n"
            "name@example.com\n\n"
            "Попробуй ещё раз или напиши /cancel."
        )
        return

    try:
        rows = await check_user(kind, value)

    except Exception:
        await message.answer(
            "⚠️ Ошибка соединения с базой. Попробуй позже."
        )
        raise

    await state.clear()

    if rows:
        row = rows[0]

        await message.answer(
            "🔴 <b>Найдена подтверждённая запись</b>\n\n"
            f"Идентификатор: <code>{escape(value)}</code>\n"
            f"Категория: {escape(str(row.get('scam_type') or 'Не указана'))}\n"
            f"Жалоб: {int(row.get('report_count') or 1)}\n"
            f"Описание: {escape(str(row.get('description') or 'Нет описания'))}\n\n"
            "Будь осторожен при взаимодействии с этим аккаунтом.",
            reply_markup=main_menu()
        )

    else:
        await message.answer(
            "🟢 Совпадений не найдено.\n\n"
            "Это не гарантирует безопасность пользователя: "
            "информации о нём может просто не быть в базе.",
            reply_markup=main_menu()
        )