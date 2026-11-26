from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import add_report
from config import ADMIN_IDS
from aiogram import Bot

router = Router()


class ReportForm(StatesGroup):
    identifier = State()
    scam_type = State()
    description = State()


@router.message(F.text == "🚨 Сообщить о мошеннике")
async def report_start(message: Message, state: FSMContext):

    await state.set_state(ReportForm.identifier)

    await message.answer(
        "🚨 <b>НОВАЯ ЖАЛОБА</b>\n\n"
        "Отправь никнейм, Telegram ID, "
        "телефон или почту подозреваемого.",
        parse_mode="HTML"
    )


@router.message(ReportForm.identifier)
async def report_identifier(message: Message, state: FSMContext):

    from handlers.check import detect_type

    identifier_type, identifier = detect_type(message.text)

    if not identifier_type:
        await message.answer("❌ Неверный формат. Попробуй ещё раз.")
        return

    await state.update_data(
        target_type=identifier_type,
        target_value=identifier
    )

    await state.set_state(ReportForm.scam_type)

    await message.answer(
        "Какой вид мошенничества?\n\n"
        "Например:\n"
        "• Мошенничество с подарками\n"
        "• Фишинг\n"
        "• Криптовалюта\n"
        "• Обман при продаже\n"
        "• Другое"
    )


@router.message(ReportForm.scam_type)
async def report_type(message: Message, state: FSMContext):

    await state.update_data(
        scam_type=message.text
    )

    await state.set_state(ReportForm.description)

    await message.answer(
        "Опиши подробно, что произошло.\n\n"
        "Расскажи, как именно тебя пытались обмануть."
    )


@router.message(ReportForm.description)
async def report_description(
    message: Message,
    state: FSMContext,
    bot: Bot
):

    await state.update_data(
        description=message.text
    )

    data = await state.get_data()

    data["reporter_id"] = message.from_user.id
    data["status"] = "pending"
    data["evidence"] = []

    await add_report(data)

    await state.clear()

    await message.answer(
        "✅ <b>ЖАЛОБА ОТПРАВЛЕНА!</b>\n\n"
        "Она поступила администрации "
        "ATKA A-Scam.\n\n"
        "Статус: 🟡 На проверке.",
        parse_mode="HTML"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                "🚨 <b>НОВАЯ ЖАЛОБА</b>\n\n"
                f"Объект: {data['target_value']}\n"
                f"Тип: {data['scam_type']}\n"
                f"Описание: {data['description']}\n"
                f"Отправитель ID: {data['reporter_id']}",
                parse_mode="HTML"
            )
        except Exception:
            pass