from aiogram.utils import executor
from aiogram import Dispatcher
from admin_logic import *
from utils import process_name, Player
from init import bot
from spy import deal_cards, PLAYERS_NUM


@dp.message_handler(state=None)
async def cmd_start(message: types.Message):
    await Player.start.set()
    await message.reply("""Добро пожаловать в Клуб Мафии "Castellano"! Что Вас интересует?""", reply_markup=base_markup)


@dp.message_handler(state="*", commands='start')
async def cmd_start(message: types.Message):
    await Player.start.set()
    await message.reply("""Добро пожаловать в Клуб Мафии "Castellano"! Что Вас интересует?""", reply_markup=base_markup)


@dp.message_handler(lambda message: message.text not in [NEAREST_GAME_BUTTON, MAFIA_BUTTON, BOARD_GAMES_BUTTON], state=Player.start)
async def process_start_invalid(message: types.Message):
    return await message.reply("Нажмите, пожалуйста, на кнопку.", reply_markup=base_markup)


@dp.message_handler(lambda message: message.text == REGISTRATION_BUTTON, state=Player.nearest_game)
async def register(message: types.Message):
    """
    Conversation's entry point
    """

    if db.id_registered(message.from_user.id):
        nick = db.get_registered_nickname(message.from_user.id)
        await message.reply(f'Вы уже зарегистрированы под ником "{nick}".\n\nХотите сняться с регистрации?"',
                    reply_markup=yes_no_markup)
        await Player.unregister.set()
    elif db.count_registered_players() >= get_max_number():
        await Player.start.set()
        await message.reply("К сожалению регистрация на ближайшую игру закрыта. Мы будем рады видеть Вас на следующей игре!",
                            reply_markup=base_markup)
    else:
        await Player.nickname.set()
        await message.reply("Для регистрации впишите, пожалуйста, свой ник.",
                            reply_markup=cancel_markup)


@dp.message_handler(lambda message: message.text == YES_BUTTON, state=Player.unregister)
async def unregister(message: types.Message):
    nick = db.get_registered_nickname(message.from_user.id)
    db.unregister_player(message.from_user.id)
    players_cnt = db.count_registered_players()
    await message.reply(f"Снятие с регистрации прошло успешно.\nБез Вас будет скучно, {nick}! :(", reply_markup=base_markup)
    report_text = f"Игрок снялся с регистрации.\n\nНикнейм: {nick}\nUsername: @{message.from_user.username}\n\nСвободных мест: {get_max_number() - players_cnt}"
    for user_id in [436612042, 334756630]:
        await bot.send_message(user_id, report_text)
    await Player.start.set()


@dp.message_handler(lambda message: message.text == NO_BUTTON, state=Player.unregister)
async def unregister(message: types.Message):
    await Player.start.set()
    await message.reply("Ок, возвращаемся в главное меню.", reply_markup=base_markup)


@dp.message_handler(lambda message: message.text == CANCEL_BUTTON, state=[Player.nickname, Player.nearest_game, Player.mafia, Player.board_games])
async def cancel_registration(message: types.Message):
    await Player.start.set()
    await message.reply("Ок, возвращаемся в главное меню.", reply_markup=base_markup)


@dp.message_handler(state=Player.nickname)
async def process_name_stage(message: types.Message):
    with open("files/game_info.txt") as file:
        game_info = file.read()
    db.register_player(message.text.replace("/", ""), message.from_user.id)
    players_cnt = db.count_registered_players()

    date = game_info.split("\n")[0].split(maxsplit=1)[1]
    time = game_info.split("\n")[1].split(maxsplit=4)[4].split(",")[0]
    address = game_info.split("\n")[2].split(maxsplit=2)[2]
    message_text = f"""Рады знакомству, {message.text}!

До встречи на игре 🤗"""
#     message_text = f"""Отлично, {message.text}! Регистрация прошла успешно.\n
# Для регистрации друга обратитесь к @naya_vokhidova\n\nЖдем Вас {date} в {time} по адресу {address}."""
    await message.reply(message_text, reply_markup=base_markup)
    report_text = f"Игрок зарегистрировался\n\nНикнейм: {message.text}\nФИО: {message.from_user.full_name}\nUsername: @{message.from_user.username}\n\nСвободных мест: {get_max_number() - players_cnt}"
    for user_id in [436612042, 334756630]:
        await bot.send_message(user_id, report_text)
    await Player.start.set()


@dp.message_handler(lambda message: message.text == MAFIA_BUTTON, state=Player.start)
async def process_mafia(message: types.Message):
    await message.reply("Что Вас интересует?", reply_markup=mafia_markup)
    await Player.mafia.set()


@dp.message_handler(lambda message: message.text == NEAREST_GAME_BUTTON, state=Player.start)
async def get_next_game_info(message: types.Message):
    with open("files/game_info.txt") as file:
        game_info = file.read()
    participants, status = db.get_registered_players()
    participants_wrapped = []
    for num, (nickname, s) in enumerate(zip(participants, status), 1):
        line = f"{num}. " + nickname
        participants_wrapped.append(process_name(line, s))
    participants_wrapped = "```\n\n" + "\n".join(participants_wrapped) + "```"
    participants_wrapped = "\n\nЗарегистрированные участники:\n" + participants_wrapped
    empty_places = f"\n\nСвободных мест: {get_max_number() - len(participants)}"
    await message.reply(
        game_info + participants_wrapped + empty_places,
        reply_markup=nearest_game_markup,
        parse_mode="Markdown"
    )
    await Player.nearest_game.set()


@dp.message_handler(lambda message: message.text == GESTURES_BUTTON, state=Player.mafia)
async def get_gestures(message: types.Message):
    await message.reply_photo(open("files/gestures.png", 'rb'), reply_markup=mafia_markup)


@dp.message_handler(lambda message: message.text == RULES_BUTTON, state=Player.mafia)
async def get_rules(message: types.Message):
    """
    max length of message is 4096
    """
    with open("files/rules.txt") as f:
        rules = f.read()
    await message.reply(rules, parse_mode="Markdown", reply_markup=mafia_markup)


@dp.message_handler(lambda message: message.text == VOTE_BUTTON, state=Player.mafia)
async def start_voting(message: types.Message):
    text = """Советую нажать на эту кнопку тогда, когда об этом скажет Госпожа Ведущая 😉"""
    await message.reply(text)


# @dp.message_handler(lambda message: message.text == BOARD_GAMES_BUTTON, state=Player.start)
# async def process_board_games(message: types.Message):
#     text = """Представляете, скоро мы будем играть в настольные игры! Уже даже кнопку специальную сделали 😎"""
#     await message.reply(text)


# @dp.message_handler(lambda message: message.text == SUBSCRIBE_BUTTON, state=Player.start)
# async def add_subscriber(message: types.Message, state: FSMContext):
#     if not db.subscriber_exists(message.from_user.id):
#         db.add_subscriber(message.from_user)
#         await message.reply("Вы успешно подписались на обновления 🤗", reply_markup=base_markup)
#     else:
#         await message.reply("Вы уже подписаны 💁‍♀️", reply_markup=base_markup)
#     await Player.start.set()


@dp.message_handler(lambda message: message.text == BOARD_GAMES_BUTTON, state=Player.start)
async def process_board_games(message: types.Message):
    await message.reply(".", reply_markup=board_games_markup)
    await Player.board_games.set()


@dp.message_handler(lambda message: message.text == PLAYER_SPY_BUTTON, state=Player.board_games)
async def process_spy_button(message: types.Message):
    players_num = await redis.get(PLAYERS_NUM) if await redis.exists(PLAYERS_NUM) else 0
    players_num = int(players_num)
    if players_num == 0:
        await message.reply("Эту кнопку нужно нажимать, когда скажет ведущая.")
    else:
        await message.reply(".", reply_markup=player_spy_markup)
        await Player.spy.set()



@dp.message_handler(lambda message: message.text == GET_CARD_BUTTON, state=Player.spy)
async def process_getting_card(message: types.Message):
    if db.spy_player_exists(message.from_user.id):
        await message.reply("У Вас отлично получается нажимать на кнопку! А кто-то ещё ни разу не нажал, представляете? Их и ждём 🤫", reply_markup=board_games_markup)
    else:
        db.add_spy_player(message.from_user.id)
        players_num = db.count_spy_players()
        target_players_num = int(await redis.get(PLAYERS_NUM))
        assert target_players_num >= players_num, f"target_players_num < players_num, {target_players_num} < {players_num}"
        await message.reply("Ждем остальных. Как только все игроки нажмут кнопку, игра начнется.", reply_markup=board_games_markup)
        if target_players_num == players_num:
            players = db.get_spy_players()
            await deal_cards(players, players_num, bot)
    await Player.board_games.set()



@dp.message_handler(lambda message: message.text == CANCEL_BUTTON, state=Player.spy)
async def process_cancel(message: types.Message):
    await message.reply(".", reply_markup=board_games_markup)
    await Player.board_games.set()


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(
        dp,
        skip_updates=True,
        on_shutdown=shutdown
    )
