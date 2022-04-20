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
from datetime import datetime

from sqlighter import SQLighter
from buttons import (
    REGISTRATION_BUTTON,
    INFO_BUTTON,
    NEAREST_GAME_BUTTON,
    RULES_BUTTON,
    GESTURES_BUTTON,
    SUBSCRIBE_BUTTON,
    CANCEL_BUTTON,
    YES_BUTTON,
    NO_BUTTON,
    MAILING_BUTTON,
    VIEW_SUBSCRIBERS_BUTTON,
    EXIT_ADMIN_BUTTON,
    ADD_PLAYER_BUTTON,
    REMOVE_PLAYER_BUTTON,
    VIEW_PLAYERS_BUTTON,
    MAILING_ALL_BUTTON,
    base_markup,
    info_markup,
    yes_no_markup,
    cancel_markup,
    admin_markup
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
    admin = State()
    mailing = State()
    print_players = State()
    mailing_all = State()
    test = State()


@dp.message_handler(lambda message: message.text == "Админ", state="*", user_id=[436612042, 334756630])
async def register_player(message: types.Message):
    await message.reply("Привет админам!", reply_markup=admin_markup)
    await Form.admin.set()


@dp.message_handler(lambda message: message.text == MAILING_BUTTON, state=Form.admin)
async def get_message_for_subscribers(message: types.Message):
    await message.reply("Введите текст для рассылки", reply_markup=cancel_markup)
    await Form.mailing.set()


@dp.message_handler(lambda message: message.text == VIEW_SUBSCRIBERS_BUTTON, state=Form.admin)
async def view_subscribers(message: types.Message):
    result = []
    for first_name, last_name, username, time in db.get_subscribers_rows():
        row = (str(first_name), str(last_name), str(username), datetime.fromtimestamp(time).date().__str__())
        result.append(" ".join(row))
    result = "\n\n".join(result)
    await message.reply(result, reply_markup=admin_markup)


@dp.message_handler(lambda message: message.text == EXIT_ADMIN_BUTTON, state=Form.admin)
async def return_to_main_menu(message: types.Message):
    await message.reply("Теперь ты снова как все пользователи 🙈", reply_markup=base_markup)
    await Form.start.set()


@dp.message_handler(lambda message: message.text == CANCEL_BUTTON, state=Form.mailing)
async def return_to_admin_menu(message: types.Message):
    await message.reply("Возврат в меню админа", reply_markup=admin_markup)
    await Form.admin.set()


@dp.message_handler(lambda message: message.text == CANCEL_BUTTON, state=Form.mailing_all)
async def return_to_admin_menu(message: types.Message):
    await message.reply("Возврат в меню админа", reply_markup=admin_markup)
    await Form.admin.set()


@dp.message_handler(state=Form.mailing)
async def dispatch_mailing(message: types.Message):
    subscribers = db.get_subscribers()
    for user in subscribers:
        await bot.send_message(user, message.text)
    await message.reply("Рассылка разослана.", reply_markup=admin_markup)
    await Form.admin.set()


@dp.message_handler(lambda message: message.text == VIEW_PLAYERS_BUTTON, state=Form.admin)
async def view_all_players(message: types.Message):
    players = db.get_all_players_nicks()
    await message.reply("\n".join(players), reply_markup=admin_markup)


@dp.message_handler(lambda message: message.text == MAILING_ALL_BUTTON, state=Form.admin)
async def get_message_for_subscribers(message: types.Message):
    await message.reply("Введите текст для рассылки всем игрокам", reply_markup=cancel_markup)
    await Form.mailing_all.set()


@dp.message_handler(state=Form.mailing_all)
async def dispatch_mailing_to_all(message: types.Message):
    players = db.get_all_players_ids()
    for user in players:
        await bot.send_message(user, message.text)
    await message.reply("Рассылка разослана.", reply_markup=admin_markup)
    await Form.admin.set()


@dp.message_handler(lambda message: message.text == ADD_PLAYER_BUTTON, state=Form.admin)
async def register_player(message: types.Message):
    await message.reply("Введите никнейм игрока для регистрации", reply_markup=types.ReplyKeyboardRemove())
    await Form.register_player.set()


@dp.message_handler(lambda message: message.text == REMOVE_PLAYER_BUTTON, state=Form.admin)
async def unregister_player_register(message: types.Message):
    players = db.get_registered_players()
    players_buttons = types.InlineKeyboardMarkup()
    for p in players:
        nickname_button = types.InlineKeyboardButton(p, callback_data=f"{p}|nickname")
        players_buttons.add(nickname_button)
    await message.reply(
        f"""Кого ты хочешь убрать?""",
        reply_markup=players_buttons,
    )


@dp.callback_query_handler(lambda c: c.data.endswith("nickname"), state=Form.admin)
async def process_callback_player_remove(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    nickname = callback_query.data.split("|")[0]
    db.unregister_player(nickname=nickname)
    await bot.send_message(
        callback_query.from_user.id,
        f"""Игрок с никнеймом "{nickname}" успешно снят с регистрации.""", reply_markup=admin_markup
    )
    await Form.admin.set()


@dp.message_handler(state=Form.register_player)
async def enter_player_nickname(message: types.Message):
    nick = message.text.replace("/", "").replace("|", "")
    db.register_player(nick)
    await Form.admin.set()
    await message.reply(f'''Игрок "{nick}" успешно зарегистрирован.''', reply_markup=admin_markup)


@dp.message_handler(state="*", commands='u', user_id=[436612042, 334756630])
async def unregister_player_register(message: types.Message):
    await message.reply(
        f"""Введите никнейм игрока для снятия с регистрации.""",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await Form.unregister_player.set()


@dp.message_handler(state=Form.unregister_player)
async def enter_player_nickname_unregister(message: types.Message):
    nick = message.text
    if db.nickname_registered(nick):
        db.unregister_player(nickname=nick)
        await message.reply(f"""Игрок с никнеймом "{nick}" успешно снят с регистрации.""", reply_markup=admin_markup)
    else:
        await message.reply(f"""Игрок с никнеймом "{nick}" не зарегистрирован.""", reply_markup=admin_markup)

    await Form.admin.set()


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
    await message.reply("""Добро пожаловать в Клуб Мафии "Castellano"! Что Вас интересует?""", reply_markup=base_markup)


@dp.message_handler(state="*", commands='start')
async def cmd_start(message: types.Message):
    await Form.start.set()
    await message.reply("""Добро пожаловать в Клуб Мафии "Castellano"! Что Вас интересует?""", reply_markup=base_markup)


@dp.message_handler(lambda message: message.text not in [REGISTRATION_BUTTON, INFO_BUTTON, SUBSCRIBE_BUTTON], state=Form.start)
async def process_start_invalid(message: types.Message):
    return await message.reply("Нажмите, пожалуйста, на кнопку.", reply_markup=base_markup)


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

# !!!ЗАГЛУШКА!!!
# @dp.message_handler(state=Form.nickname)
# async def process_name(message: types.Message, state: FSMContext):
#     message_text = f"""{message.text}, для подтверждения регистрации отправьте 500₽ на номер +79139422767 (Тинькофф).
# В комментарии к переводу напишите свой никнейм."""
#     db.register_player(message.text.replace("/", ""), message.from_user.id)
#     await message.reply(message_text, reply_markup=base_markup)
#     players_cnt = db.count_registered_players()
#     report_text = f"Игрок зарегистрировался\n\nНикнейм: {message.text}\nUsername: @{message.from_user.username}\n\nСвободных мест: {get_max_number() - players_cnt}"
#     for user_id in [436612042, 334756630]:
#         await bot.send_message(user_id, report_text)
#     await Form.start.set()


@dp.message_handler(state=Form.nickname)
async def process_name(message: types.Message, state: FSMContext):
    with open("game_info.txt") as file:
        game_info = file.read()
    db.register_player(message.text.replace("/", ""), message.from_user.id)
    players_cnt = db.count_registered_players()

    date = game_info.split("\n")[0].split(maxsplit=1)[1]
    time = game_info.split("\n")[1].split(maxsplit=4)[4].split(",")[0]
    address = game_info.split("\n")[2].split(maxsplit=2)[2]
    message_text = f"""Отлично, {message.text}! Для завершения регистрации оплатите игровой вечер по номеру +79139422767 на Сбербанк/Тинькофф с указанием никнейма"""
#     message_text = f"""Отлично, {message.text}! Регистрация прошла успешно.\n
# Для регистрации друга обратитесь к @naya_vokhidova\n\nЖдем Вас {date} в {time} по адресу {address}."""
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


@dp.message_handler(lambda message: message.text == SUBSCRIBE_BUTTON, state=Form.start)
async def add_subscriber(message: types.Message, state:FSMContext):
    if not db.subscriber_exists(message.from_user.id):
        db.add_subscriber(message.from_user)
        await message.reply("Вы успешно подписались на обновления 🤗", reply_markup=base_markup)
    else:
        await message.reply("Вы уже подписаны 💁‍♀️", reply_markup=base_markup)
    await Form.start.set()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
