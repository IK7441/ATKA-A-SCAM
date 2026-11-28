from html import escape

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import ADMIN_IDS

from database import (
    get_statistics,
    get_latest,
    get_pending_reports,
    get_report,
    approve_report,
    reject_report
)

from keyboards.menu import admin_menu, main_menu

router = Router()


def is_admin(user_id):
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_command(message: Message):

    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещён.")
        return

    await message.answer(
        "🛠 <b>Панель администратора</b>",
        reply_markup=admin_menu()
    )


@router.message(Command("stats"))
@router.message(F.text == "📊 Статистика")
async def stats_handler(message: Message):

    stats = await get_statistics()

    await message.answer(
        "📊 <b>Статистика ATKA A-Scam</b>\n\n"
        f"Записей в базе: {stats['scammers']}\n"
        f"Всего жалоб: {stats['reports']}\n"
        f"Ожидают проверки: {stats['pending']}"
    )


@router.message(F.text == "📥 Ожидают проверки")
async def pending_handler(message: Message):

    if not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещён.")
        return

    reports = await get_pending_reports()

    if not reports:
        await message.answer("📭 Ожидающих жалоб нет.")
        return

    for report in reports:
        await message.answer(
            f"🚨 <b>Жалоба #{report['id']}</b>\n\n"
            f"Объект: <code>{escape(str(report['target_value']))}</code>\n"
            f"Категория: {escape(str(report['scam_type']))}\n"
            f"Описание: {escape(str(report['description']))}"
        )


@router.message(Command("pending"))
async def pending_command(message: Message):
    await pending_handler(message)


@router.message(F.text == "🆕 Последние записи")
async def latest_handler(message: Message):

    records = await get_latest()

    if not records:
        await message.answer("Пока нет подтверждённых записей.")
        return

    for row in records:
        await message.answer(
            "🔴 <b>Запись базы</b>\n\n"
            f"Идентификатор: <code>{escape(str(row.get('identifier_value') or ''))}</code>\n"
            f"Категория: {escape(str(row.get('scam_type') or 'Не указана'))}\n"
            f"Жалоб: {int(row.get('report_count') or 1)}"
        )


@router.message(F.text == "⬅️ Главное меню")
async def back_menu(message: Message):

    await message.answer(
        "Главное меню.",
        reply_markup=main_menu()
    )


# Одобрение и отклонение жалоб

@router.callback_query(F.data.startswith("report:"))
async def moderate_report(callback: CallbackQuery, bot: Bot):

    if not is_admin(callback.from_user.id):
        await callback.answer(
            "У тебя нет доступа.",
            show_alert=True
        )
        return

    try:
        _, action, raw_id = callback.data.split(":")

        report_id = int(raw_id)

        report = await get_report(report_id)

        if not report:
            await callback.answer(
                "Жалоба не найдена.",
                show_alert=True
            )
            return

        if report["status"] != "pending":
            await callback.answer(
                "Эта жалоба уже обработана.",
                show_alert=True
            )
            return

        if action == "approve":

            await approve_report(report)

            result = "✅ Жалоба одобрена."

        elif action == "reject":

            await reject_report(report_id)

            result = "❌ Жалоба отклонена."

        else:
            await callback.answer("Неизвестное действие.")
            return

        await callback.message.edit_reply_markup(
            reply_markup=None
        )

        await callback.message.answer(result)

        try:
            await bot.send_message(
                report["reporter_id"],
                f"Результат рассмотрения жалобы #{report_id}:\n{result}"
            )
        except Exception:
            pass

        await callback.answer("Готово!")

    except Exception:
        await callback.answer(
            "Ошибка обработки жалобы.",
            show_alert=True
        )
        raise