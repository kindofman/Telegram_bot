from buttons import admin_markup
from aiogram import types
from aiogram.dispatcher.filters.state import State
from init import dp, db, bot, Form
from typing import Callable


def process_name(name, status):
    if status == 0:
        suffix = ""
    elif status == 1:
        suffix = " ✅"
    elif status == 2:
        suffix = " 🆕"
    return f"{name:{19}}{suffix}"

def create_inline_buttons(
        allowed_statuses: list,
        identifier: str,
        action: Callable,
        trigger_button: str,
        state: State,
        markup: types.ReplyKeyboardMarkup,
        reply_message: str = ".",
):
    async def process_trigger(message: types.Message):
        players, status = db.get_registered_players()
        players_buttons = types.InlineKeyboardMarkup()
        for p, s in zip(players, status):
            if s not in allowed_statuses:
                continue
            button_name = process_name(p, s)
            nickname_button = types.InlineKeyboardButton(button_name, callback_data=f"{p}|{identifier}")
            players_buttons.add(nickname_button)
        await message.reply(
            reply_message,
            reply_markup=players_buttons,
        )

    async def process_callback(callback_query: types.CallbackQuery):
        await bot.answer_callback_query(callback_query.id)
        nickname = callback_query.data.split("|")[0]
        action(nickname=nickname)
        await bot.send_message(
            callback_query.from_user.id,
            f"""Действие для игрока "{nickname}" выполнено.""", reply_markup=markup
        )

    dp.message_handler(lambda message: message.text == trigger_button, state=state)(process_trigger)
    dp.callback_query_handler(lambda c: c.data.endswith(identifier), state=state)(process_callback)

def get_max_number():
    with open("max_number.txt") as file:
        return int(file.read())
