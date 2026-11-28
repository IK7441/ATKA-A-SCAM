from html import escape

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS
from database import add_report
from handlers.check import detect_type
from keyboards.menu import main_menu

router = Router()


class ReportForm(StatesGroup):
    identifier = State()
    category = State()
    description = State()


@router.message(Command("report"))
@router.message(F.text == "🚨 Сообщить о мошеннике")
async def report_start(message: Message, state: FSMContext):

    await state.clear()
    await state.set_state(ReportForm.identifier)

    await message.answer(
        "🚨 <b>Создание жалобы</b>\n\n"
        "Отправь username, Telegram ID, телефон или email.\n\n"
        "Не отправляй пароли и коды подтверждения."
    )


@router.message(ReportForm.identifier)
async def report_identifier(message: Message, state: FSMContext):

    kind, value = detect_type(message.text or "")

    if not kind:
        await message.answer(
            "❌ Неверный формат. Попробуй ещё раз."
        )
        return

    await state.update_data(
        target_type=kind,
        target_value=value
    )

    await state.set_state(ReportForm.category)

    await message.answer(
        "Теперь укажи категорию мошенничества.\n\n"
        "Например: фишинг, продажа, криптовалюта, "
        "вымогательство или другое."
    )


@router.message(ReportForm.category)
async def report_category(message: Message, state: FSMContext):

    category = (message.text or "").strip()

    if len(category) < 2 or len(category) > 80:
        await message.answer(
            "Категория должна содержать от 2 до 80 символов."
        )
        return

    await state.update_data(scam_type=category)

    await state.set_state(ReportForm.description)

    await message.answer(
        "Опиши ситуацию.\n\n"
        "Минимум 10 символов, максимум 2000."
    )


@router.message(ReportForm.description)
async def report_description(
    message: Message,
    state: FSMContext,
    bot: Bot
):

    description = (message.text or "").strip()

    if len(description) < 10 or len(description) > 2000:
        await message.answer(
            "Описание должно содержать от 10 до 2000 символов."
        )
        return

    data = await state.get_data()

    report_data = {
        "reporter_id": message.from_user.id,
        "target_type": data["target_type"],
        "target_value": data["target_value"],
        "scam_type": data["scam_type"],
        "description": description,
        "evidence": [],
        "status": "pending"
    }

    try:
        saved = await add_report(report_data)

    except Exception:
        await message.answer(
            "⚠️ Не удалось сохранить жалобу. "
            "Попробуй позже."
        )
        raise

    await state.clear()

    await message.answer(
        "✅ Жалоба успешно отправлена!\n\n"
        "Она ожидает проверки администратора.",
        reply_markup=main_menu()
    )

    if not saved:
        return

    report_id = saved["id"]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Одобрить",
                    callback_data=f"report:approve:{report_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"report:reject:{report_id}"
                )
            ]
        ]
    )

    admin_text = (
        "🚨 <b>НОВАЯ ЖАЛОБА</b>\n\n"
        f"Номер: <code>{report_id}</code>\n"
        f"Объект: <code>{escape(data['target_value'])}</code>\n"
        f"Тип: {escape(data['target_type'])}\n"
        f"Категория: {escape(data['scam_type'])}\n"
        f"Описание: {escape(description)}\n"
        f"Отправитель: <code>{message.from_user.id}</code>"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                admin_text,
                reply_markup=keyboard
            )
        except Exception:
            pass