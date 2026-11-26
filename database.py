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


async def run_query(query):
    return await asyncio.to_thread(query.execute)


async def register_user(user):
    return await run_query(
        db.table("users").upsert({
            "telegram_id": user.id,
            "username": user.username
        }, on_conflict="telegram_id")
    )


async def check_user(identifier_type, identifier):
    result = await run_query(
        db.table("scammers")
        .select("*")
        .eq("identifier_type", identifier_type)
        .eq("identifier_value", identifier)
        .limit(1)
    )

    return result.data


async def add_report(data):
    return await run_query(
        db.table("reports").insert(data)
    )


async def approve_report(report):
    await run_query(
        db.table("scammers").upsert({
            "identifier_type": report["target_type"],
            "identifier_value": report["target_value"],
            "scam_type": report["scam_type"],
            "description": report["description"],
            "report_count": 1
        }, on_conflict="identifier_type,identifier_value")
    )

    await run_query(
        db.table("reports")
        .update({"status": "approved"})
        .eq("id", report["id"])
    )


async def reject_report(report_id):
    return await run_query(
        db.table("reports")
        .update({"status": "rejected"})
        .eq("id", report_id)
    )


async def get_report(report_id):
    result = await run_query(
        db.table("reports")
        .select("*")
        .eq("id", report_id)
        .limit(1)
    )

    return result.data[0] if result.data else None


async def get_statistics():
    scammers = await run_query(
        db.table("scammers").select("id")
    )

    reports = await run_query(
        db.table("reports").select("id")
    )

    pending = await run_query(
        db.table("reports")
        .select("id")
        .eq("status", "pending")
    )

    return {
        "scammers": len(scammers.data),
        "reports": len(reports.data),
        "pending": len(pending.data)
    }


async def get_latest():
    result = await run_query(
        db.table("scammers")
        .select("*")
        .order("added_at", desc=True)
        .limit(10)
    )

    return result.data