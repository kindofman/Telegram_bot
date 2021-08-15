import logging
import config

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor

import argparse

from sqlighter import SQLighter
from buttons import (
    REGISTRATION_BUTTON,
    INFO_BUTTON,
    NEAREST_GAME_BUTTON,
    RULES_BUTTON,
    GESTURES_BUTTON,
    CANCEL_BUTTON,
    YES_BUTTON,
    NO_BUTTON,
    base_markup,
    info_markup,
    yes_no_markup,
    cancel_markup
)

parser = argparse.ArgumentParser(description='Mafia bot')
parser.add_argument("purpose", help="Mode", default="test", choices={"test", "prod"}, nargs="?")
args = parser.parse_args()

API_TOKEN = config.API_TOKEN_TEST if args.purpose == "test" else config.API_TOKEN_PROD

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

db = SQLighter("database.db")

def get_max_number():
    with open("max_number.txt") as file:
        return int(file.read())

# States
class Form(StatesGroup):
    start = State()
    nickname = State()  # Will be represented in storage as 'Form:nickname'
    unregister = State()
    info = State()
    change_info = State()
    max_number = State()
    reset = State()
    register_player = State()
    unregister_player = State()
    test = State()


@dp.message_handler(state="*", commands='r', user_id=[436612042, 334756630])
async def register_player(message: types.Message):
    await message.reply("Введите никнейм игрока для регистрации", reply_markup=types.ReplyKeyboardRemove())
    await Form.register_player.set()

@dp.message_handler(state=Form.register_player)
async def enter_player_nickname(message: types.Message):
    nick = message.text
    db.register_player(nick)

    await Form.start.set()
    await message.reply(f'''Игрок "{nick}" успешно зарегистрирован.''', reply_markup=base_markup)

@dp.message_handler(state="*", commands='u', user_id=[436612042, 334756630])
async def unregister_player_register(message: types.Message):
    await message.reply("Введите никнейм игрока для снятия с регистрации.", reply_markup=types.ReplyKeyboardRemove())
    await Form.unregister_player.set()

@dp.message_handler(state=Form.unregister_player)
async def enter_player_nickname_unregister(message: types.Message):
    nick = message.text
    if db.nickname_registered(nick):
        db.unregister_player(nickname=nick)
        await message.reply(f"""Игрок с никнеймом "{nick}" успешно снят с регистрации.""", reply_markup=base_markup)
    else:
        await message.reply(f"""Игрок с никнеймом "{nick}" не зарегистрирован.""", reply_markup=base_markup)

    await Form.start.set()


@dp.message_handler(state="*", commands='newgame', user_id=[436612042, 334756630])
async def get_game_settings(message: types.Message):
    with open("game_info.txt") as file:
        game_info = file.read()
    await message.reply("Введите, пожалуйста, новую информацию по следующей игре")
    await message.reply(game_info, reply_markup=types.ReplyKeyboardRemove())
    await Form.change_info.set()


@dp.message_handler(state="*", commands='maxnumber', user_id=[436612042, 334756630])
async def get_current_max_number(message: types.Message):
    max_number = get_max_number()
    await message.reply(f"Текущее максимальное число игроков {max_number}.\n\nВведите новое максимальное число игроков"
                        ,reply_markup=types.ReplyKeyboardRemove())
    await Form.max_number.set()


@dp.message_handler(state=Form.max_number)
async def change_max_number(message: types.Message):
    new_max_number = int(message.text)
    with open("max_number.txt", "w") as file:
        file.write(str(new_max_number))
    await message.reply("Максимальное число игроков успешно изменено", reply_markup=base_markup)
    await Form.start.set()


@dp.message_handler(state=Form.change_info)
async def change_game_settings(message: types.Message):
    game_info = message.text
    with open("game_info.txt", "w") as file:
        file.write(game_info)
    await message.reply("Информация по игре успешно перезаписана", reply_markup=base_markup)
    await Form.start.set()


@dp.message_handler(state="*", commands='reset', user_id=[436612042, 334756630])
async def reset_registration(message: types.Message):
    await message.reply("Вы уверены, что хотите обнулить регистрацию?", reply_markup=yes_no_markup)
    await Form.reset.set()

@dp.message_handler(lambda message: message.text == YES_BUTTON, state=Form.reset)
async def reset_registration_for_sure(message: types.Message):
    db.clear()
    await message.reply("Бот готов для регистрации участников на следующую игру", reply_markup=base_markup)
    await Form.start.set()

@dp.message_handler(lambda message: message.text == NO_BUTTON, state=Form.reset)
async def cancel_reset_registration(message: types.Message):
    await Form.start.set()
    await message.reply("Ок, возвращаемся в главное меню.", reply_markup=base_markup)

@dp.message_handler(state=None)
async def cmd_start(message: types.Message):
    await Form.start.set()
    await message.reply("Привет! Круто, что Вы здесь! Что Вас интересует?", reply_markup=base_markup)


@dp.message_handler(state="*", commands='start')
async def cmd_start(message: types.Message):
    await Form.start.set()
    await message.reply("Привет! Круто, что Вы здесь! Что Вас интересует?", reply_markup=base_markup)


@dp.message_handler(lambda message: message.text not in [REGISTRATION_BUTTON, INFO_BUTTON], state=Form.start)
async def process_start_invalid(message: types.Message):
    return await message.reply("Нажмите, пожалуйста, на одну из 2-х кнопок.", reply_markup=base_markup)


@dp.message_handler(lambda message: message.text == REGISTRATION_BUTTON, state=Form.start)
async def register(message: types.Message):
    """
    Conversation's entry point
    """

    if db.id_registered(message.from_user.id):
        nick = db.get_registered_nickname(message.from_user.id)
        await message.reply(f'Вы уже зарегистрированы под ником "{nick}".\n\nХотите сняться с регистрации?"',
                    reply_markup=yes_no_markup)
        await Form.unregister.set()
    elif db.count_registered_players() >= get_max_number():
        await Form.start.set()
        await message.reply("К сожалению регистрация на ближайшую игру закрыта. Мы будем рады видеть Вас на следующей игре!",
                            reply_markup=base_markup)
    else:
        await Form.nickname.set()
        await message.reply("Для регистрации впишите, пожалуйста, свой ник.",
                            reply_markup=cancel_markup)


@dp.message_handler(lambda message: message.text == YES_BUTTON, state=Form.unregister)
async def unregister(message: types.Message, state: FSMContext):
    print(f"id: {message.from_user.id}")
    print(f"first_name: {message.from_user.first_name}")
    print(f"last_name: {message.from_user.last_name}")
    print(f"username: {message.from_user.username}")

    nick = db.get_registered_nickname(message.from_user.id)
    db.unregister_player(message.from_user.id)
    players_cnt = db.count_registered_players()
    await message.reply(f"Снятие с регистрации прошло успешно.\nБез Вас будет скучно, {nick}! :(", reply_markup=base_markup)
    report_text = f"Игрок снялся с регистрации.\n\nНикнейм: {nick}\nUsername: @{message.from_user.username}\n\nСвободных мест: {get_max_number() - players_cnt}"
    for user_id in [436612042, 334756630]:
        await bot.send_message(user_id, report_text)
    await Form.start.set()

@dp.message_handler(lambda message: message.text == NO_BUTTON, state=Form.unregister)
async def unregister(message: types.Message, state: FSMContext):
    await Form.start.set()
    await message.reply("Ок, возвращаемся в главное меню.", reply_markup=base_markup)


@dp.message_handler(lambda message: message.text == CANCEL_BUTTON, state=Form.nickname)
async def cancel_registration(message: types.Message, state: FSMContext):
    await Form.start.set()
    await message.reply("Ок, возвращаемся в главное меню.", reply_markup=base_markup)


@dp.message_handler(state=Form.nickname)
async def process_name(message: types.Message, state: FSMContext):
    with open("game_info.txt") as file:
        game_info = file.read()
    db.register_player(message.text, message.from_user.id)
    players_cnt = db.count_registered_players()

    date = game_info.split("\n")[0].split(maxsplit=1)[1]
    time = game_info.split("\n")[1].split(maxsplit=4)[4].split(",")[0]
    address = game_info.split("\n")[2].split(maxsplit=2)[2]
    message_text = f"""Отлично, {message.text}! Регистрация прошла успешно.\n
Для регистрации друга обратитесь к @naya_vokhidova\n\nЖдем Вас {date} в {time} по адресу {address}."""
    await message.reply(message_text, reply_markup=base_markup)
    report_text = f"Игрок зарегистрировался\n\nНикнейм: {message.text}\nUsername: @{message.from_user.username}\n\nСвободных мест: {get_max_number() - players_cnt}"
    for user_id in [436612042, 334756630]:
        await bot.send_message(user_id, report_text)
    await Form.start.set()


@dp.message_handler(lambda message: message.text == INFO_BUTTON, state=Form.start)
async def get_next_game_info(message: types.Message, state: FSMContext):
    await message.reply("Что Вы хотите узнать?", reply_markup=info_markup)
    await Form.info.set()


@dp.message_handler(lambda message: message.text == NEAREST_GAME_BUTTON, state=Form.info)
async def get_next_game_info(message: types.Message, state: FSMContext):
    with open("game_info.txt") as file:
        game_info = file.read()
    participants = db.get_registered_players()
    participants_wrapped = []
    for num, nickname in enumerate(participants, 1):
        participants_wrapped.append(f"{num}. {nickname}")
    participants_wrapped = "\n".join(participants_wrapped)
    participants_wrapped = "\n\nЗарегистрированные участники\n" + participants_wrapped
    empty_places = f"\n\nСвободных мест: {get_max_number() - len(participants)}"
    await message.reply(game_info + participants_wrapped + empty_places, reply_markup=base_markup)
    await Form.start.set()

@dp.message_handler(lambda message: message.text == GESTURES_BUTTON, state=Form.info)
async def get_next_game_info(message: types.Message, state: FSMContext):
    await message.reply_photo(open("gestures.png", 'rb'), reply_markup=base_markup)
    await Form.start.set()

@dp.message_handler(lambda message: message.text == RULES_BUTTON, state=Form.info)
async def get_rules(message: types.Message, state:FSMContext):
    """
    max length of message is 4096
    """
    with open("rules.txt") as f:
        rules = f.read()
    await message.reply(rules, parse_mode="Markdown", reply_markup=base_markup)
    await Form.start.set()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
