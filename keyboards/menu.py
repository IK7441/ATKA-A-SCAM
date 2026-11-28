from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🔍 Проверить пользователя"
                )
            ],
            [
                KeyboardButton(
                    text="🚨 Сообщить о мошеннике"
                )
            ],
            [
                KeyboardButton(text="📊 Статистика"),
                KeyboardButton(text="🆕 Последние записи")
            ],
            [
                KeyboardButton(text="ℹ️ О проекте")
            ]
        ],
        resize_keyboard=True
    )


def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📥 Ожидают проверки"
                )
            ],
            [
                KeyboardButton(text="📊 Статистика"),
                KeyboardButton(text="🆕 Последние записи")
            ],
            [
                KeyboardButton(
                    text="⬅️ Главное меню"
                )
            ]
        ],
        resize_keyboard=True
    )