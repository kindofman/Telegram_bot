from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from admin_logic import *
from utils import process_name


@dp.message_handler(state=None)
async def cmd_start(message: types.Message):
    await Form.start.set()
    await message.reply("""Добро пожаловать в Клуб Мафии "Castellano"! Что Вас интересует?""", reply_markup=base_markup)


@dp.message_handler(state="*", commands='start')
async def cmd_start(message: types.Message):
    await Form.start.set()
    await message.reply("""Добро пожаловать в Клуб Мафии "Castellano"! Что Вас интересует?""", reply_markup=base_markup)


@dp.message_handler(lambda message: message.text not in [NEAREST_GAME_BUTTON, MAFIA_BUTTON, BOARD_GAMES_BUTTON], state=Form.start)
async def process_start_invalid(message: types.Message):
    return await message.reply("Нажмите, пожалуйста, на кнопку.", reply_markup=base_markup)


@dp.message_handler(lambda message: message.text == REGISTRATION_BUTTON, state=Form.nearest_game)
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


@dp.message_handler(lambda message: message.text == CANCEL_BUTTON, state=[Form.nickname, Form.nearest_game, Form.mafia])
async def cancel_registration(message: types.Message, state: FSMContext):
    await Form.start.set()
    await message.reply("Ок, возвращаемся в главное меню.", reply_markup=base_markup)


@dp.message_handler(state=Form.nickname)
async def process_name_stage(message: types.Message, state: FSMContext):
    with open("files/game_info.txt") as file:
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
    report_text = f"Игрок зарегистрировался\n\nНикнейм: {message.text}\nФИО: {message.from_user.full_name}\nUsername: @{message.from_user.username}\n\nСвободных мест: {get_max_number() - players_cnt}"
    for user_id in [436612042, 334756630]:
        await bot.send_message(user_id, report_text)
    await Form.start.set()


@dp.message_handler(lambda message: message.text == MAFIA_BUTTON, state=Form.start)
async def process_mafia(message: types.Message, state: FSMContext):
    await message.reply("Что Вы хотите узнать?", reply_markup=mafia_markup)
    await Form.mafia.set()


@dp.message_handler(lambda message: message.text == NEAREST_GAME_BUTTON, state=Form.start)
async def get_next_game_info(message: types.Message, state: FSMContext):
    with open("files/game_info.txt") as file:
        game_info = file.read()
    participants, status = db.get_registered_players()
    processed_nicks = [process_name(nick, s) for nick, s in zip(participants, status)]
    participants_wrapped = []
    for num, nickname in enumerate(processed_nicks, 1):
        participants_wrapped.append(f"{num}. {nickname}")
    participants_wrapped = "```\n\n" + "\n".join(participants_wrapped) + "```"
    participants_wrapped = "\n\nЗарегистрированные участники:\n" + participants_wrapped
    empty_places = f"\n\nСвободных мест: {get_max_number() - len(participants)}"
    await message.reply(
        game_info + participants_wrapped + empty_places,
        reply_markup=nearest_game_markup,
        parse_mode="Markdown"
    )
    await Form.nearest_game.set()


@dp.message_handler(lambda message: message.text == GESTURES_BUTTON, state=Form.mafia)
async def get_gestures(message: types.Message, state: FSMContext):
    await message.reply_photo(open("files/gestures.png", 'rb'), reply_markup=mafia_markup)


@dp.message_handler(lambda message: message.text == RULES_BUTTON, state=Form.mafia)
async def get_rules(message: types.Message, state: FSMContext):
    """
    max length of message is 4096
    """
    with open("files/rules.txt") as f:
        rules = f.read()
    await message.reply(rules, parse_mode="Markdown", reply_markup=mafia_markup)


@dp.message_handler(lambda message: message.text == VOTE_BUTTON, state=Form.mafia)
async def start_voting(message: types.Message):
    text = """Советую нажать на эту кнопку тогда, когда об этом скажет Госпожа Ведущая 😉"""
    await message.reply(text)


@dp.message_handler(lambda message: message.text == BOARD_GAMES_BUTTON, state=Form.start)
async def process_board_games(message: types.Message):
    text = """Представляете, скоро мы будем играть в настольные игры! Уже даже кнопку специальную сделали 😎"""
    await message.reply(text)


@dp.message_handler(lambda message: message.text == SUBSCRIBE_BUTTON, state=Form.start)
async def add_subscriber(message: types.Message, state: FSMContext):
    if not db.subscriber_exists(message.from_user.id):
        db.add_subscriber(message.from_user)
        await message.reply("Вы успешно подписались на обновления 🤗", reply_markup=base_markup)
    else:
        await message.reply("Вы уже подписаны 💁‍♀️", reply_markup=base_markup)
    await Form.start.set()



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
