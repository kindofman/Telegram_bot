from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
from aiogram.dispatcher import FSMContext
from asyncio import sleep
from random import choice, randint

from databases import db_wrapper
from loader import dp, bot
from typing import Callable


DATE = "date"
ADMIN = "Админ"


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


def date_to_info(date: str):
    preposition = "во" if date.startswith("вторник") else "в"
    weekdays = ["понедельник,", "вторник,", "среду,", "четверг,", "пятницу,", "субботу,", "воскресенье,"]
    weekday, day, month = date.split()
    for w in weekdays:
        if w[:3] == weekday[:3]:
            weekday = w
    return f"""Спортивка {preposition} {weekday} {day} {month}
⏳ Старт стола - 19:00
🧭 Место: Моховая 10 (вход с Литейного 11)
💸 Стоимость: 400₽
🕴️Ведущая: Селена 💪🏻"""


async def make_Naya_happy(message: types.Message):
    words = (
        'удивительная', 'внимательная', 'красивая', 'лучшая', 'успешная', 'заботливая', 'милая', 'прекрасная',
        'умная', 'шикарная', 'обалденная', 'очаровашка', 'любимая', 'весёлая', 'нежная', 'яркая', 'прелестная',
        'приятная', 'сладкая', 'дивная', 'ангельская', 'добрая', 'бесподобная', 'волшебная', 'крутышка', 'смелая',
        'ласковая', 'романтичная', 'великолепная', 'внимательная', 'страстная', 'игривая', 'единственная',
        'стройная', 'безумная', 'симпатичная', 'изящная', 'талантливая', 'элегантная', 'чуткая', 'уникальная',
    )
    await __rabbit(message)
    bot_message = await message.answer('<b>Крошечные напоминания того, что ты...</b>', parse_mode="HTML")
    await sleep(2)

    for word in words:
        await bot_message.edit_text(f'<b>Cамая {word}✨</b>', parse_mode="HTML")
        await sleep(0.5)

    await bot_message.edit_text(f'<b> Ная = the best🤗</b>', parse_mode="HTML")


async def __rabbit(message: types.Message):
    left_eyes = '┈┃▋▏▋▏┃┈'
    right_eyes = '┈┃╱▋╱▋┃┈'
    img = [
        '╭━━╮╭━━╮',
        '╰━╮┃┃╭━╯',
        '┈╭┛┗┛┗╮┈',
        '┈┃╱▋╱▋┃┈',
        '╭┛▔▃▔┈┗╮',
        '╰┓╰┻━╯┏╯',
        '╭┛┈┏┓┈┗╮',
        '╰━━╯╰━━╯',
    ]
    eyes = choice((True, False))
    img[3] = right_eyes if eyes else left_eyes
    bot_message = await play_stroke_anim(message, img)
    await sleep(1)

    for _ in range(randint(5, 10)):
        eyes = not eyes
        img[3] = right_eyes if eyes else left_eyes
        await bot_message.edit_text('\n'.join(img))
        await sleep(0.5)

async def play_stroke_anim(msg: types.Message, anims, tick=0.1):
    bot_message = await msg.answer("Привет!")
    for i in range(len(anims)):
        data = "\n".join(anims[0:i + 1])
        await bot_message.edit_text(data)
        await sleep(tick)
    return bot_message

