from utils import (
    create_inline_buttons,
    get_max_number,
    Admin,
    Player,
)
from init import dp, db, redis, bot
from buttons import *
from spy import LOCATIONS_REDIS, PLAYERS_NUM, deal_cards



@dp.message_handler(lambda message: message.text == "Админ", state="*", user_id=[436612042, 334756630])
async def enter_admin_menu(message: types.Message):
    await message.reply("Привет админам!", reply_markup=admin_markup)
    await Admin.main.set()


# @dp.message_handler(lambda message: message.text == MAILING_BUTTON, state=Admin.main)
# async def get_message_for_subscribers(message: types.Message):
#     await message.reply("Введите текст для рассылки", reply_markup=cancel_markup)
#     await Admin.mailing.set()


# @dp.message_handler(lambda message: message.text == VIEW_SUBSCRIBERS_BUTTON, state=Admin.main)
# async def view_subscribers(message: types.Message):
#     result = []
#     for first_name, last_name, username, time in db.get_subscribers_rows():
#         row = (str(first_name), str(last_name), str(username), datetime.fromtimestamp(time).date().__str__())
#         result.append(" ".join(row))
#     result = "\n\n".join(result)
#     await message.reply(result, reply_markup=admin_markup)


@dp.message_handler(lambda message: message.text == EXIT_ADMIN_BUTTON, state=Admin.main)
async def return_to_main_menu(message: types.Message):
    await message.reply("Теперь ты снова как все пользователи 🙈", reply_markup=base_markup)
    await Player.start.set()


@dp.message_handler(lambda message: message.text == CANCEL_BUTTON, state=[Admin.players, Admin.new_game])
async def return_to_admin_menu(message: types.Message):
    await message.reply("Возврат в меню админа", reply_markup=admin_markup)
    await Admin.main.set()


# @dp.message_handler(state=Admin.mailing)
# async def dispatch_mailing(message: types.Message):
#     subscribers = db.get_subscribers()
#     for user in subscribers:
#         await bot.send_message(user, message.text)
#     await message.reply("Рассылка разослана.", reply_markup=admin_markup)
#     await Admin.main.set()


# @dp.message_handler(lambda message: message.text == MAILING_ALL_BUTTON, state=Admin.main)
# async def get_message_for_subscribers(message: types.Message):
#     await message.reply("Введите текст для рассылки всем игрокам", reply_markup=cancel_markup)
#     await Admin.mailing_all.set()


# @dp.message_handler(state=Admin.mailing_all)
# async def dispatch_mailing_to_all(message: types.Message):
#     players = db.get_all_players_ids()
#     for user in players:
#         await bot.send_message(user, message.text)
#     await message.reply("Рассылка разослана.", reply_markup=admin_markup)
#     await Admin.main.set()


@dp.message_handler(lambda message: message.text == ADD_PLAYER_BUTTON, state=Admin.players)
async def register_player(message: types.Message):
    await message.reply("Введите никнейм игрока для регистрации", reply_markup=types.ReplyKeyboardRemove())
    await Admin.register_player.set()


@dp.message_handler(state=Admin.register_player)
async def enter_player_nickname(message: types.Message):
    nick = message.text.replace("/", "").replace("|", "")
    db.register_player(nick)
    await Admin.players.set()
    await message.reply(f'''Игрок "{nick}" успешно зарегистрирован.''', reply_markup=players_markup)


create_inline_buttons(
    allowed_statuses=[0, 1, 2],
    identifier="remove",
    action=db.unregister_player,
    trigger_button=REMOVE_PLAYER_BUTTON,
    state=Admin.players,
    markup=players_markup,
)

create_inline_buttons(
    allowed_statuses=[0, 1],
    identifier="payment",
    action=db.change_payment_state,
    trigger_button=PAYMENT_VERIFIED_BUTTON,
    state=Admin.players,
    markup=players_markup,
)

create_inline_buttons(
    allowed_statuses=[0, 2],
    identifier="newby",
    action=db.change_newby_state,
    trigger_button=NEWBY_STATE_BUTTON,
    state=Admin.players,
    markup=players_markup,
)


@dp.message_handler(lambda message: message.text == NEW_GAME_BUTTON, state=Admin.main)
async def process_new_game_button(message: types.Message):
    await message.reply(f".", reply_markup=new_game_markup)
    await Admin.new_game.set()


@dp.message_handler(lambda message: message.text == PLAYERS_BUTTON, state=Admin.main)
async def process_players_button(message: types.Message):
    await message.reply(".", reply_markup=players_markup)
    await Admin.players.set()


@dp.message_handler(lambda message: message.text == INFO_BUTTON, state=Admin.new_game)
async def get_game_settings(message: types.Message):
    with open("files/game_info.txt") as file:
        game_info = file.read()
    await message.reply("Введите, пожалуйста, новую информацию по следующей игре")
    await message.reply(game_info, reply_markup=types.ReplyKeyboardRemove())
    await Admin.change_info.set()


@dp.message_handler(state=Admin.change_info)
async def change_game_settings(message: types.Message):
    game_info = message.text
    with open("files/game_info.txt", "w") as file:
        file.write(game_info)
    await message.reply("Информация по игре успешно перезаписана", reply_markup=new_game_markup)
    await Admin.new_game.set()


@dp.message_handler(lambda message: message.text == MAX_PLAYERS_BUTTON, state=Admin.new_game)
async def get_current_max_number(message: types.Message):
    max_number = get_max_number()
    await message.reply(f"Текущее максимальное число игроков {max_number}.\n\nВведите новое максимальное число игроков"
                        , reply_markup=types.ReplyKeyboardRemove())
    await Admin.max_number.set()


@dp.message_handler(state=Admin.max_number)
async def change_max_number(message: types.Message):
    new_max_number = int(message.text)
    with open("files/max_number.txt", "w") as file:
        file.write(str(new_max_number))
    await message.reply("Максимальное число игроков успешно изменено", reply_markup=new_game_markup)
    await Admin.new_game.set()


@dp.message_handler(lambda message: message.text == RESET_BUTTON, state=Admin.new_game)
async def reset_registration(message: types.Message):
    await message.reply("Вы уверены, что хотите обнулить регистрацию?", reply_markup=yes_no_markup)
    await Admin.reset.set()


@dp.message_handler(lambda message: message.text == YES_BUTTON, state=Admin.reset)
async def reset_registration_for_sure(message: types.Message):
    db.clear()
    await message.reply("Бот готов для регистрации участников на следующую игру", reply_markup=new_game_markup)
    await Admin.new_game.set()


@dp.message_handler(lambda message: message.text == NO_BUTTON, state=Admin.reset)
async def cancel_reset_registration(message: types.Message):
    await Admin.new_game.set()
    await message.reply("Ок, возвращаемся в главное меню.", reply_markup=new_game_markup)


@dp.message_handler(lambda message: message.text == CANCEL_BUTTON, state=Admin.players)
async def cancel_reset_registration(message: types.Message):
    await Admin.new_game.set()
    await message.reply("Ок, возвращаемся в главное меню.", reply_markup=new_game_markup)


@dp.message_handler(lambda message: message.text == ADMIN_SPY_BUTTON, state=Admin.main)
async def process_spy_button(message: types.Message):
    await message.reply(".", reply_markup=admin_spy_markup)
    await Admin.spy.set()


@dp.message_handler(lambda message: message.text == START_BUTTON, state=Admin.spy)
async def process_spy_start(message: types.Message):
    await message.reply("Введите кол-во участников для игры", reply_markup=cancel_markup)
    await Admin.spy_num_players.set()


@dp.message_handler(lambda message: message.text == CANCEL_BUTTON, state=Admin.spy_num_players)
async def process_return(message: types.Message):
    await message.reply(".", reply_markup=admin_spy_markup)
    await Admin.spy.set()


@dp.message_handler(lambda message: message.text == STOP_BUTTON, state=Admin.spy)
async def process_spy_stop(message: types.Message):
    await redis.set(PLAYERS_NUM, "0")
    db.clear_spy_table()
    await message.reply("Игра в шпиона обнулена")


@dp.message_handler(lambda message: message.text == REPEAT_BUTTON, state=Admin.spy)
async def process_spy_stop(message: types.Message):
    players = db.get_spy_players()
    players_num = int(await redis.get(PLAYERS_NUM))
    await deal_cards(players, players_num, bot)
    await message.reply("Розданы карты с новой локацией")


@dp.message_handler(lambda message: message.text == CANCEL_BUTTON, state=Admin.spy)
async def process_return(message: types.Message):
    await message.reply(".", reply_markup=admin_markup)
    await Admin.main.set()


@dp.message_handler(state=Admin.spy_num_players)
async def process_spy_num_players(message: types.Message):
    try:
        num_players = int(message.text)
        if num_players <= 0:
            await message.reply("Нужно ввести положительное число")
        else:
            await redis.set(PLAYERS_NUM, str(num_players))
            await message.reply("Бот готов для начала игры!", reply_markup=admin_markup)
            await Admin.main.set()
    except ValueError:
        await message.reply("Вы не ввели целое число")
    db.clear_spy_table()
