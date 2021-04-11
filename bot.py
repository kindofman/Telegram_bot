import logging
import config

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
import pickle
<<<<<<< Updated upstream
=======
import argparse
from sqlighter import SQLighter

parser = argparse.ArgumentParser(description='Mafia bot')
parser.add_argument("purpose", help="Mode", default="test", choices={"test", "prod"}, nargs="?")
args = parser.parse_args()

API_TOKEN = config.API_TOKEN_TEST if args.purpose == "test" else config.API_TOKEN_PROD
>>>>>>> Stashed changes

logging.basicConfig(level=logging.INFO)

API_TOKEN = config.API_TOKEN


bot = Bot(token=API_TOKEN)
db = SQLighter("database.db")

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

<<<<<<< Updated upstream
MAX_NUMBER = 14
game_info = """Игра в среду, 17 марта
⏳ Время сбора - 18:00, старт стола - 18:30
🕵🏻‍♂️ 3 игры за вечер
🧭 Место: Щербаков пер, 12к2, Lounge Bar "111 Metrov"
💸 Стоимость: 300₽

Зарегистрированные участники
"""

=======
MAX_NUMBER = 16
>>>>>>> Stashed changes

# States
class Form(StatesGroup):
    start = State()
    nickname = State()  # Will be represented in storage as 'Form:nickname'
    unregister = State()
    info = State()
    test = State()

base_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
base_markup.add("Правила")
base_markup.add("Регистрация")
base_markup.add("Инфо")

info_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
info_markup.add("Информация по игре")
info_markup.add("Жесты")

<<<<<<< Updated upstream
# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='reset')
@dp.message_handler(Text(equals='reset', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return
=======
yes_no_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
yes_no_markup.add("Да", "Нет")


@dp.message_handler(state="*", commands='register', user_id=[436612042, 334756630])
async def register_player(message: types.Message):
    await message.reply("Введите никнейм игрока для регистрации", reply_markup=types.ReplyKeyboardRemove())
    await Form.register_player.set()

@dp.message_handler(state=Form.register_player)
async def enter_player_nickname(message: types.Message):
    nick = message.text
    if db.nickname_registered(nick):
        await message.reply(f"""Игрок "{nick}" уже зарегистрирован.""", reply_markup=base_markup)
    else:
        db.register_player(nickname=nick)
        await message.reply(f'''Игрок "{nick}" успешно зарегистрирован.''', reply_markup=base_markup)
    await Form.start.set()

@dp.message_handler(state="*", commands='unregister', user_id=[436612042, 334756630])
async def unregister_player_register(message: types.Message):
    await message.reply("Введите никнейм игрока для снятия с регистрации.", reply_markup=types.ReplyKeyboardRemove())
    await Form.unregister_player.set()

@dp.message_handler(state=Form.unregister_player)
async def enter_player_nickname_unregister(message: types.Message):
    nick = message.text
    if db.nickname_registered(nick):
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

@dp.message_handler(lambda message: message.text == "Да", state=Form.reset)
async def reset_registration_for_sure(message: types.Message):
    db.clear()
    await message.reply("Бот готов для регистрации участников на следующую игру", reply_markup=base_markup)
    await Form.start.set()

@dp.message_handler(lambda message: message.text == "Нет", state=Form.reset)
async def cancel_reset_registration(message: types.Message):
    await Form.start.set()
    await message.reply("Ок, возвращаемся в главное меню.", reply_markup=base_markup)
>>>>>>> Stashed changes

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Бот перезагружен успешно.', reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state="*", commands='start')
async def cmd_start(message: types.Message):
    # Configure ReplyKeyboardMarkup

    await Form.start.set()
    await message.reply("Привет! Круто, что ты здесь! Что тебя интересует?", reply_markup=base_markup)

@dp.message_handler(lambda message: message.text not in ["Регистрация", "Правила", "Инфо"], state=Form.start)
async def process_start_invalid(message: types.Message):
    """
    In this example gender has to be one of: Male, Female, Other.
    """
    return await message.reply("Нажмите, пожалуйста, на одну из 3-ех кнопок.")

@dp.message_handler(lambda message: message.text == "Регистрация", state=Form.start)
async def register(message: types.Message):
    """
    Conversation's entry point
    """
<<<<<<< Updated upstream

    with open("ids.pkl", "rb") as file:
        ids = pickle.load(file)
    # Set state
    if message.from_user.id in ids:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
        markup.add("Да", "Нет")
        await message.reply(f'Вы уже зарегистрированы под ником "{ids[message.from_user.id]}".\n\nХочется сняться с регистрации?"',
                            reply_markup=markup)
        await Form.unregister.set()

=======
    # Set state
    if db.id_registered(message.from_user.id):
        nick = db.get_registered_nickname(message.from_user.id)
        await message.reply(f'Вы уже зарегистрированы под ником "{nick}".\n\nХотите сняться с регистрации?"',
                            reply_markup=yes_no_markup)
        await Form.unregister.set()
    elif db.count_registered_players() >= MAX_NUMBER:
        await Form.start.set()
        await message.reply("К сожалению регистрация на ближайшую игру закрыта. Мы будем рады видеть Вас на следующей игре!",
        reply_markup=base_markup)
>>>>>>> Stashed changes
    else:
        await Form.nickname.set()
        await message.reply("Для регистрации впишите, пожалуйста, свой ник.",
                            reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(lambda message: message.text == "Да", state=Form.unregister)
async def unregister(message: types.Message, state: FSMContext):
<<<<<<< Updated upstream
    with open("ids.pkl", "rb") as file:
        ids = pickle.load(file)
    nick = ids[message.from_user.id]
    del ids[message.from_user.id]
    with open("ids.pkl", 'wb') as output:
        pickle.dump(ids, output, pickle.HIGHEST_PROTOCOL)
    with open("participants.pkl", 'rb') as file:
        participants = pickle.load(file)
    index = len(participants) - 1 - participants[::-1].index(nick)
    del participants[index]

    with open("participants.pkl", 'wb') as output:
        pickle.dump(participants, output, pickle.HIGHEST_PROTOCOL)
    await message.reply(f"Снятие с регистрации прошло успешно.\nБез вас будет скучно, {nick}! :(", reply_markup=base_markup)
=======
    nick = db.get_registered_nickname(message.from_user.id)
    db.unregister_player(message.from_user.id)
    await message.reply(f"Снятие с регистрации прошло успешно.\nБез Вас будет скучно, {nick}! :(", reply_markup=base_markup)
>>>>>>> Stashed changes
    await Form.start.set()

@dp.message_handler(lambda message: message.text == "Нет", state=Form.unregister)
async def unregister(message: types.Message, state: FSMContext):
    await Form.start.set()
    await message.reply("Ок, возвращаемся в главное меню.", reply_markup=base_markup)

@dp.message_handler(state=Form.nickname)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
<<<<<<< Updated upstream
    with open("ids.pkl", "rb") as file:
        ids = pickle.load(file)
    ids[message.from_user.id] = message.text
    with open("ids.pkl", 'wb') as output:
        pickle.dump(ids, output, pickle.HIGHEST_PROTOCOL)

    with open("participants.pkl", 'rb') as file:
        participants = pickle.load(file)
    participants.append(message.text)
    with open("participants.pkl", 'wb') as output:
        pickle.dump(participants, output, pickle.HIGHEST_PROTOCOL)
    await message.reply(f"Отлично, {message.text}! Регистрация прошла успешно.", reply_markup=base_markup)
=======
    db.register_player(message.text, message.from_user.id)
    await message.reply(f"Отлично, {message.text}! Регистрация прошла успешно.\n\nДля регистрации друга обратитесь к @naya_vokhidova",
                        reply_markup=base_markup)
>>>>>>> Stashed changes
    await Form.start.set()
    # await state.finish()
    # await Form.next()

@dp.message_handler(lambda message: message.text == "Инфо", state=Form.start)
async def get_next_game_info(message: types.Message, state: FSMContext):
    await message.reply("Что вы хотите узнать?", reply_markup=info_markup)
    await Form.info.set()

@dp.message_handler(lambda message: message.text == "Информация по игре", state=Form.info)
async def get_next_game_info(message: types.Message, state: FSMContext):
<<<<<<< Updated upstream
    with open("participants.pkl", 'rb') as file:
        participants = pickle.load(file)
    print(message.from_user.id)
=======
    with open("game_info.txt") as file:
        game_info = file.read()
    participants = db.get_registered_players()
>>>>>>> Stashed changes
    participants_wrapped = []
    for num, nickname in enumerate(participants, 1):
        participants_wrapped.append(f"{num}. {nickname}")
    participants_wrapped = "\n".join(participants_wrapped)
    empty_places = f"\n\nСвободных мест: {MAX_NUMBER - len(participants)}"
    await message.reply(game_info + participants_wrapped + empty_places, reply_markup=base_markup)
    await Form.start.set()

@dp.message_handler(lambda message: message.text == "Жесты", state=Form.info)
async def get_next_game_info(message: types.Message, state: FSMContext):
    await message.reply_photo(open("gestures.png", 'rb'), reply_markup=base_markup)
    await Form.start.set()

@dp.message_handler(lambda message: message.text == "Правила", state=Form.start)
async def get_rules(message: types.Message, state:FSMContext):
    """
    max length of message is 4096
    """
    with open("rules.txt") as f:
        rules = f.read()
    await message.reply(rules, parse_mode="Markdown")

@dp.message_handler(state=Form.test)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = message.text

        # Remove keyboard
        markup = types.ReplyKeyboardRemove()

        # And send message
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Hi! Nice to meet you,', md.bold(data['name'])),
                md.text('Age:', md.code(data['age'])),
                md.text('Gender:', data['gender']),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )

    # Finish conversation
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
