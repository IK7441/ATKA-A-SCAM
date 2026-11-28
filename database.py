import asyncio

from supabase import create_client

from config import (
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)

db = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY
)


async def execute(query):
    return await asyncio.to_thread(query.execute)


# Регистрация пользователя

async def register_user(user):
    return await execute(
        db.table("users").upsert(
            {
                "telegram_id": user.id,
                "username": user.username
            },
            on_conflict="telegram_id"
        )
    )


# Проверка пользователя

async def check_user(identifier_type, identifier_value):
    result = await execute(
        db.table("scammers")
        .select("*")
        .eq("identifier_type", identifier_type)
        .eq("identifier_value", identifier_value)
        .limit(1)
    )

    return result.data or []


# Добавление жалобы

async def add_report(data):
    result = await execute(
        db.table("reports").insert(data)
    )

    return result.data[0] if result.data else None


# Получение жалобы

async def get_report(report_id):
    result = await execute(
        db.table("reports")
        .select("*")
        .eq("id", report_id)
        .limit(1)
    )

    return result.data[0] if result.data else None


# Ожидающие жалобы

async def get_pending_reports(limit=10):
    result = await execute(
        db.table("reports")
        .select("*")
        .eq("status", "pending")
        .order("created_at", desc=True)
        .limit(limit)
    )

    return result.data or []


# Обновление статуса жалобы

async def set_report_status(report_id, status):
    return await execute(
        db.table("reports")
        .update({"status": status})
        .eq("id", report_id)
    )


# Одобрение жалобы

async def approve_report(report):
    existing = await check_user(
        report["target_type"],
        report["target_value"]
    )

    if existing:
        row = existing[0]

        await execute(
            db.table("scammers")
            .update({
                "report_count": int(
                    row.get("report_count") or 0
                ) + 1
            })
            .eq("id", row["id"])
        )

    else:
        await execute(
            db.table("scammers").insert({
                "identifier_type": report["target_type"],
                "identifier_value": report["target_value"],
                "scam_type": report["scam_type"],
                "description": report["description"],
                "report_count": 1
            })
        )

    await set_report_status(report["id"], "approved")


# Отклонение жалобы

async def reject_report(report_id):
    return await set_report_status(
        report_id,
        "rejected"
    )


# Статистика

async def get_statistics():
    scammers = await execute(
        db.table("scammers")
        .select("id", count="exact")
    )

    reports = await execute(
        db.table("reports")
        .select("id", count="exact")
    )

    pending = await execute(
        db.table("reports")
        .select("id", count="exact")
        .eq("status", "pending")
    )

    return {
        "scammers": scammers.count or 0,
        "reports": reports.count or 0,
        "pending": pending.count or 0
    }


# Последние записи

async def get_latest(limit=10):
    result = await execute(
        db.table("scammers")
        .select("*")
        .order("added_at", desc=True)
        .limit(limit)
    )

    return result.data or []