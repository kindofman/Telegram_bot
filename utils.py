from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from loader import dp, db, bot
from typing import Callable


# States
class Player(StatesGroup):
    start = State()
    nickname = State()  # Will be represented in storage as 'Form:nickname'
    unregister = State()
    nearest_game = State()
    mafia = State()
    board_games = State()
    spy = State()

class Admin(StatesGroup):
    change_info = State()
    max_number = State()
    reset = State()
    register_player = State()
    main = State()
    # mailing = State()
    # print_players = State()
    # mailing_all = State()
    new_game = State()
    players = State()
    spy = State()
    spy_num_players = State()


def process_name(name, status):
    if status == 0:
        suffix = ""
    elif status == 1:
        suffix = " ✅"
    elif status == 2:
        suffix = " 🆕"
    return f"{name:{20}}{suffix}"

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
    with open("files/max_number.txt") as file:
        return int(file.read())
