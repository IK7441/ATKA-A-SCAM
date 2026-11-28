import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()

SUPABASE_SERVICE_ROLE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY", ""
).strip()

ADMIN_IDS = {
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "7313596236").split(",")
    if x.strip().isdigit()
}


def validate_config():
    missing = []

    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")

    if not SUPABASE_URL:
        missing.append("SUPABASE_URL")

    if not SUPABASE_SERVICE_ROLE_KEY:
        missing.append("SUPABASE_SERVICE_ROLE_KEY")

    if missing:
        raise RuntimeError(
            "Не заданы переменные окружения: "
            + ", ".join(missing)
        )