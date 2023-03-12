from loader import db, bot, redis
from common.utils import Player, process_name, DATE, ADMIN
from buttons import *
from spy import deal_cards, PLAYERS_NUM
from databases import db_wrapper

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext


LIMIT_NICKNAME = 15


async def start_menu(message: types.Message):
    await Player.start.set()
    await message.reply("""Добро пожаловать в Клуб интеллектуальных игр Castellano!

Что Вас интересует?
""", reply_markup=base_markup)


async def cmd_start(message: types.Message):
    await Player.start.set()
    await message.reply("""Добро пожаловать в Клуб интеллектуальных игр Castellano!

Что Вас интересует?
""", reply_markup=base_markup)


async def process_start_invalid(message: types.Message):
    return await message.reply("Нажмите, пожалуйста, на кнопку.", reply_markup=base_markup)


async def register(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        date = data[DATE]
    game = await db_wrapper.get_game(date)
    players = game[db_wrapper.Game.players]
    max_players = game[db_wrapper.Game.max_players]
    player = [p for p in players if p.id == message.from_user.id]
    if player:
        nick = player[0].nick
        await message.reply(f'Вы уже зарегистрированы под ником "{nick}".\n\nХотите сняться с регистрации?"',
                    reply_markup=yes_no_markup)
        await Player.unregister.set()
    elif len(players) >= max_players:
        await Player.start.set()
        await message.reply(
            "К сожалению регистрация на эту игру закрыта.", reply_markup=base_markup,
        )
    else:
        await Player.nickname.set()
        await message.reply(
            "Для регистрации впишите, пожалуйста, свой никнейм.", reply_markup=cancel_markup,
        )


async def unregister(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        date = data[DATE]
    game = await db_wrapper.get_game(date)
    players = game[db_wrapper.Game.players]
    max_players = game[db_wrapper.Game.max_players]
    player = [p for p in players if p.id == message.from_user.id][0]
    await db_wrapper.remove_player_by_id(date, message.from_user.id)
    players_cnt = len(players) - 1
    await message.reply(
        f"Понял, снял с регистрации.\nНадеюсь, что Вы посетите нас на следующих играх 😊", reply_markup=base_markup,
    )
    report_text = f"Игрок снялся с регистрации на {date}.\n\nНикнейм: {player.nick}\nUsername: @{message.from_user.username}\n\nСвободных мест: {max_players - players_cnt}"
    for user_id in [436612042, 334756630]:
        await bot.send_message(user_id, report_text)
    await Player.start.set()


async def skip_unregister(message: types.Message):
    await Player.start.set()
    await message.reply("Ок, возвращаемся в главное меню.", reply_markup=base_markup)


async def cancel_registration(message: types.Message):
    await Player.start.set()
    await message.reply("Ок, возвращаемся в главное меню.", reply_markup=base_markup)


async def process_name_stage(message: types.Message, state: FSMContext):
    nickname = message.text.replace("/", "")[:LIMIT_NICKNAME]
    async with state.proxy() as data:
        date = data[DATE]
    await db_wrapper.add_player_by_id(date, message.from_user.id, nickname)
    game = await db_wrapper.get_game(date)
    players_cnt = len(game[db_wrapper.Game.players])
    max_players = game[db_wrapper.Game.max_players]
    message_text = f"""Сделано!
До встречи на игре, {message.text} 🤗"""
    await message.reply(message_text, reply_markup=base_markup)
    report_text = (
        f"Игрок зарегистрировался, {date}\n\nНикнейм: {message.text}\nФИО: {message.from_user.full_name}\n"
        f"Username: @{message.from_user.username}\n\nСвободных мест: {max_players - players_cnt}"
    )
    for user_id in [436612042, 334756630]:
        await bot.send_message(user_id, report_text)
    await Player.start.set()


async def process_mafia(message: types.Message):
    await message.reply("Что Вас интересует?", reply_markup=mafia_markup)
    await Player.mafia.set()


async def process_nearest_game(message: types.Message):
    existing_games = await db_wrapper.get_all_games()
    buttons = [[i] for i in existing_games] + [[CANCEL_BUTTON]]
    if existing_games:
        await message.reply(
            "Выберите дату встречи.",
            reply_markup=types.ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        )
        await Player.select_date.set()
    else:
        await message.reply("Запись сейчас закрыта. Но мы скоро запланируем новые встречи!🤗", reply_markup=base_markup)
        await Player.start.set()

async def get_next_game_info(message: types.Message, state: FSMContext):
    date = message.text
    async with state.proxy() as data:
        data[DATE] = date
    game = await db_wrapper.get_game(date)
    if game is None:
        await message.reply("Вы точно нажали кнопку?🧐", reply_markup=base_markup)
        await Player.start.set()

    game_info = game[db_wrapper.Game.info]
    players = game[db_wrapper.Game.players]
    participants_wrapped = []
    for num, p in enumerate(players, 1):
        participants_wrapped.append(f"{num}. " + process_name(p))

    participants_wrapped = "```\n\n" + "\n".join(participants_wrapped) + "```"
    participants_wrapped = "\n\nЗарегистрированные участники:\n" + participants_wrapped
    empty_places = f"\n\nСвободных мест: {await db_wrapper.get_max_players(date) - len(players)}"
    await message.reply(
        game_info + participants_wrapped + empty_places,
        reply_markup=nearest_game_markup,
        parse_mode="Markdown"
    )
    await Player.nearest_game.set()


async def get_gestures(message: types.Message):
    await message.reply_photo(open("files/gestures.png", 'rb'), reply_markup=mafia_markup)


async def get_rules(message: types.Message):
    """
    max length of message is 4096
    """
    with open("files/rules.txt") as f:
        rules = f.read()
    await message.reply(rules, parse_mode="Markdown", reply_markup=mafia_markup)


async def start_voting(message: types.Message):
    text = """Советую нажать на эту кнопку тогда, когда об этом скажет Госпожа Ведущая 😉"""
    await message.reply(text)


async def process_board_games(message: types.Message):
    await message.reply(".", reply_markup=board_games_markup)
    await Player.board_games.set()


async def process_spy_button(message: types.Message):
    players_num = await redis.get(PLAYERS_NUM) if await redis.exists(PLAYERS_NUM) else 0
    players_num = int(players_num)
    if players_num == 0:
        await message.reply("Эту кнопку нужно нажимать, когда скажет ведущая.")
    else:
        await message.reply(".", reply_markup=player_spy_markup)
        await Player.spy.set()


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


async def process_cancel(message: types.Message):
    await message.reply(".", reply_markup=board_games_markup)
    await Player.board_games.set()


def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start_menu, state=None)
    dp.register_message_handler(cmd_start, state="*", commands='start')
    dp.register_message_handler(
        process_start_invalid,
        lambda message: message.text not in [NEAREST_GAME_BUTTON, MAFIA_BUTTON, BOARD_GAMES_BUTTON, ADMIN],
        state=Player.start,
    )
    dp.register_message_handler(
        register, lambda message: message.text == REGISTRATION_BUTTON, state=Player.nearest_game,
    )
    dp.register_message_handler(unregister, lambda message: message.text == YES_BUTTON, state=Player.unregister)
    dp.register_message_handler(skip_unregister, lambda message: message.text == NO_BUTTON, state=Player.unregister)
    dp.register_message_handler(
        cancel_registration,
        lambda message: message.text == CANCEL_BUTTON,
        state=[Player.nickname, Player.nearest_game, Player.mafia, Player.board_games, Player.select_date],
    )
    dp.register_message_handler(process_name_stage, state=Player.nickname)
    dp.register_message_handler(process_mafia, lambda message: message.text == MAFIA_BUTTON, state=Player.start)
    dp.register_message_handler(
        process_nearest_game, lambda message: message.text == NEAREST_GAME_BUTTON, state=Player.start,
    )
    dp.register_message_handler(
        get_next_game_info, lambda message: message.text != CANCEL_BUTTON, state=Player.select_date,
    )
    dp.register_message_handler(get_gestures, lambda message: message.text == GESTURES_BUTTON, state=Player.mafia)
    dp.register_message_handler(get_rules, lambda message: message.text == RULES_BUTTON, state=Player.mafia)
    dp.register_message_handler(start_voting, lambda message: message.text == VOTE_BUTTON, state=Player.mafia)
    dp.register_message_handler(
        process_board_games, lambda message: message.text == BOARD_GAMES_BUTTON, state=Player.start,
    )
    dp.register_message_handler(
        process_spy_button, lambda message: message.text == PLAYER_SPY_BUTTON, state=Player.board_games,
    )
    dp.register_message_handler(process_getting_card, lambda message: message.text == GET_CARD_BUTTON, state=Player.spy)
    dp.register_message_handler(process_cancel, lambda message: message.text == CANCEL_BUTTON, state=Player.spy)

