from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.dispatcher import FSMContext

import db_wrapper
from loader import dp, db, bot
from typing import Callable
from datetime import datetime


DATE = "date"
DATE_STARTS = "20"


# States
class Player(StatesGroup):
    start = State() # Ближайшая игра, Мафия, Настолки
    select_date = State() # Даты созданных игр
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
    main = State() # Новая игра, регистрация, мафия, шпион
    new_game = State() # Создать игру, Изменить игру
    create_game = State() # даты для создания игры
    change_game = State() # даты созданных игр
    change_game_for_date = State() # инфо, кол-во игроков, удалить игру
    players = State() # даты созданных игр
    players_for_date = State() #Добавить, Убрать, Оплачено?, Новый игрок
    spy = State()
    spy_num_players = State()


def process_name(player):
    if player.status == db_wrapper.Status.unknown:
        suffix = ""
    elif player.status == db_wrapper.Status.paid:
        suffix = " ✅"
    elif player.status == db_wrapper.Status.new:
        suffix = " 🆕"
    return f"{player.nick:{20}}{suffix}"

def create_inline_buttons(
        allowed_statuses: list,
        identifier: str,
        action: Callable,
        trigger_button: str,
        state_group: State,
        markup: types.ReplyKeyboardMarkup,
        reply_message: str = ".",
):
    async def process_trigger(message: types.Message, state: FSMContext):
        # players, status = db.get_registered_players()
        async with state.proxy() as data:
            date = data[DATE]
        players = await db_wrapper.get_registered_players(date)
        players_buttons = types.InlineKeyboardMarkup()
        for p in players:
            if p.status.value not in allowed_statuses:
                continue
            button_name = process_name(p)
            nickname_button = types.InlineKeyboardButton(button_name, callback_data=f"{p.nick}|{identifier}")
            players_buttons.add(nickname_button)
        await message.reply(
            reply_message,
            reply_markup=players_buttons,
        )

    async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
        await bot.answer_callback_query(callback_query.id)
        nick = callback_query.data.split("|")[0]
        async with state.proxy() as data:
            date = data[DATE]
        await action(date=date, nick=nick)
        await bot.send_message(
            callback_query.from_user.id,
            f"""Действие для игрока "{nick}" выполнено.""", reply_markup=markup
        )

    dp.register_message_handler(process_trigger, lambda message: message.text == trigger_button, state=state_group)
    dp.callback_query_handler(lambda c: c.data.endswith(identifier), state=state_group)(process_callback)

def date_to_weekday(date: str):
    weekday = datetime.strptime(date, '%Y-%m-%d').isoweekday()
    return ["пн", "вт", "ср", "чт", "пт", "сб", "вс"][weekday - 1]


def date_to_info(date: str):
    date = datetime.strptime(date, '%Y-%m-%d')
    weekday = date.isoweekday()
    insertion_weekday = [
        "в понедельник", "во вторник", "в среду", "в четверг", "в пятницу", "в субботу", "в воскресение",
    ][weekday - 1]
    insertion_month = [
        'января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'
    ][date.month - 1]

    return f"""Спортивка {insertion_weekday}, {date.day} {insertion_month}
⏳ Старт стола - 19:00
🧭 Место: Моховая 10 (вход с Литейного 11)
💸 Стоимость: 400₽
🕴️Ведущая: Селена 💪🏻"""


def get_max_number():
    with open("files/max_number.txt") as file:
        return int(file.read())

