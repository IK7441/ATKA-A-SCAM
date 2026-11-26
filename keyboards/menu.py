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
                KeyboardButton(
                    text="📊 Статистика"
                ),
                KeyboardButton(
                    text="🆕 Последние скамеры"
                )
            ],
            [
                KeyboardButton(
                    text="ℹ️ О проекте"
                )
            ]
        ],
        resize_keyboard=True
    )