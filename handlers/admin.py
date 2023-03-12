import types
from aiogram.dispatcher import FSMContext

from databases import db_wrapper
from common.time_utils import get_dates_ahead, is_date_button
from common.utils import (
    create_inline_buttons,
    make_Naya_happy,
    Admin,
    Player,
    DATE,
    ADMIN,
)
from loader import db, redis, bot
from buttons import *
from aiogram import Dispatcher
from spy import PLAYERS_NUM, deal_cards


DAYS_SHOW = 14
EXISTS = "exists"
start_kb = types.ReplyKeyboardMarkup(resize_keyboard=True,)
start_kb.row('Navigation Calendar', 'Dialog Calendar')


async def enter_admin_menu(message: types.Message):
    # await make_Naya_happy(message)

    await message.reply("Привет админам!", reply_markup=admin_markup)
    await Admin.main.set()


async def return_to_main_menu(message: types.Message):
    await message.reply("Теперь ты снова как все пользователи 🙈", reply_markup=base_markup)
    await Player.start.set()


async def return_to_admin_menu(message: types.Message):
    await message.reply("Возврат в меню админа", reply_markup=admin_markup)
    await Admin.main.set()


async def register_player(message: types.Message):
    await message.reply("Введите никнейм игрока для регистрации", reply_markup=types.ReplyKeyboardRemove())
    await Admin.register_player.set()


async def enter_player_nickname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        date = data[DATE]
    nick = message.text.replace("/", "").replace("|", "")
    await db_wrapper.add_player_by_nick(date, nick)
    await Admin.players_for_date.set()
    await message.reply(f'''Игрок "{nick}" успешно зарегистрирован.''', reply_markup=players_markup)


create_inline_buttons(
    allowed_statuses=[0, 1, 2],
    identifier="remove",
    action=db_wrapper.remove_player_by_nick,
    trigger_button=REMOVE_PLAYER_BUTTON,
    state_group=Admin.players_for_date,
    markup=players_markup,
)

create_inline_buttons(
    allowed_statuses=[0, 1],
    identifier="payment",
    action=db_wrapper.change_payment_state,
    trigger_button=PAYMENT_VERIFIED_BUTTON,
    state_group=Admin.players_for_date,
    markup=players_markup,
)

create_inline_buttons(
    allowed_statuses=[0, 2],
    identifier="newby",
    action=db_wrapper.change_newby_state,
    trigger_button=NEWBY_STATE_BUTTON,
    state_group=Admin.players_for_date,
    markup=players_markup,
)


async def process_new_game_button(message: types.Message):
    await message.reply(f"..", reply_markup=new_game_markup)
    await Admin.new_game.set()


async def create_game(message: types.Message):
    days_ahead = get_dates_ahead(DAYS_SHOW)
    existing_games = await db_wrapper.get_all_games()
    buttons = []
    for i in range(DAYS_SHOW // 2):
        left = days_ahead[i] if days_ahead[i] not in existing_games else EXISTS
        right = days_ahead[(DAYS_SHOW // 2) + i]
        right = right if right not in existing_games else EXISTS
        buttons.append([left])
        buttons[i].append(right)
    markup = types.ReplyKeyboardMarkup(buttons)
    await message.reply(f"..", reply_markup=markup)
    await Admin.create_game.set()


async def create_game_for_date(message: types.Message):
    await db_wrapper.create_game(message.text)
    await message.reply(f"Игра на дату {message.text} создана.", reply_markup=new_game_markup)
    await Admin.new_game.set()


async def change_game(message: types.Message):
    existing_games = await db_wrapper.get_all_games()
    if existing_games:
        await message.reply("..", reply_markup=types.ReplyKeyboardMarkup([[i] for i in existing_games]))
        await Admin.change_game.set()
    else:
        await message.reply(f"Открытых игр нет.", reply_markup=new_game_markup)
        await Admin.new_game.set()


async def change_game_for_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date'] = message.text
    await message.reply(f"{message.text}", reply_markup=change_game_markup)
    await Admin.change_game_for_date.set()


async def process_new_game_button(message: types.Message):
    await message.reply(f"..", reply_markup=new_game_markup)
    await Admin.new_game.set()


async def process_players_button(message: types.Message):
    existing_games = await db_wrapper.get_all_games()
    buttons = [[i] for i in existing_games] + [[CANCEL_BUTTON]]
    await message.reply("..", reply_markup=types.ReplyKeyboardMarkup(buttons, resize_keyboard=True))
    await Admin.players.set()


async def set_date_for_players(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data[DATE] = message.text
    await message.reply(f"Регистрация на {message.text}.", reply_markup=players_markup)
    await Admin.players_for_date.set()


async def get_game_settings(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        date = data[DATE]
    game_info = await db_wrapper.get_info(date)
    await message.reply("Введите, пожалуйста, новую информацию по следующей игре")
    await message.reply(game_info, reply_markup=types.ReplyKeyboardRemove())
    await Admin.change_info.set()


async def change_game_settings(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        date = data[DATE]
    game_info = message.text
    await db_wrapper.change_info(date, game_info)
    await message.reply("Информация по игре успешно перезаписана", reply_markup=change_game_markup)
    await Admin.change_game_for_date.set()


async def get_current_max_number(message: types.Message, state: FSMContext):
    date = (await state.get_data())[DATE]
    max_number = await db_wrapper.get_max_players(date)
    await message.reply(f"Текущее максимальное число игроков {max_number}.\n\nВведите новое максимальное число игроков"
                        , reply_markup=types.ReplyKeyboardRemove())
    await Admin.max_number.set()


async def change_max_number(message: types.Message, state: FSMContext):
    new_max_number = int(message.text)
    date = (await state.get_data())[DATE]
    await db_wrapper.change_max_players(date, new_max_number)
    await message.reply("Максимальное число игроков успешно изменено", reply_markup=change_game_markup)
    await Admin.change_game_for_date.set()


async def reset_registration(message: types.Message):
    await message.reply("Вы уверены, что хотите удалить игру?", reply_markup=yes_no_markup)
    await Admin.reset.set()


async def reset_registration_for_sure(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        date = data[DATE]

    await db_wrapper.delete_game(date)
    await message.reply(f"Игра на {date} удалена.", reply_markup=new_game_markup)
    await Admin.new_game.set()


async def no_reset_registration(message: types.Message):
    await Admin.new_game.set()
    await message.reply("Ок, возвращаемся в главное меню.", reply_markup=new_game_markup)


async def cancel_reset_registration(message: types.Message):
    await Admin.new_game.set()
    await message.reply("Ок, возвращаемся в главное меню.", reply_markup=new_game_markup)


async def process_spy_button(message: types.Message):
    await message.reply("..", reply_markup=admin_spy_markup)
    await Admin.spy.set()


async def process_spy_start(message: types.Message):
    await message.reply("Введите кол-во участников для игры", reply_markup=cancel_markup)
    await Admin.spy_num_players.set()


async def process_return_admin(message: types.Message):
    await message.reply("..", reply_markup=admin_spy_markup)
    await Admin.spy.set()


async def process_spy_stop(message: types.Message):
    await redis.set(PLAYERS_NUM, "0")
    db.clear_spy_table()
    await message.reply("Игра в шпиона обнулена")


async def process_spy_repeat(message: types.Message):
    players = db.get_spy_players()
    players_num = int(await redis.get(PLAYERS_NUM))
    await deal_cards(players, players_num, bot)
    await message.reply("Розданы карты с новой локацией")


async def process_return_spy(message: types.Message):
    await message.reply("..", reply_markup=admin_markup)
    await Admin.main.set()


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

def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        enter_admin_menu, lambda message: message.text == ADMIN, state="*", user_id=[436612042, 334756630],
    )
    dp.register_message_handler(
        return_to_main_menu, lambda message: message.text == EXIT_ADMIN_BUTTON, state=Admin.main,
    )
    dp.register_message_handler(
        return_to_admin_menu, lambda message: message.text == CANCEL_BUTTON, state=[
            Admin.players, Admin.players_for_date, Admin.new_game, Admin.change_game_for_date,
        ],
    )
    dp.register_message_handler(
        register_player, lambda message: message.text == ADD_PLAYER_BUTTON, state=Admin.players_for_date,
    )
    dp.register_message_handler(enter_player_nickname, state=Admin.register_player)
    dp.register_message_handler(
        process_new_game_button, lambda message: message.text == NEW_GAME_BUTTON, state=Admin.main,
    )
    dp.register_message_handler(create_game, lambda message: message.text == CREATE_GAME_BUTTON, state=Admin.new_game)
    dp.register_message_handler(
        process_players_button, lambda message: message.text == PLAYERS_BUTTON, state=Admin.main,
    )
    dp.register_message_handler(
        get_game_settings, lambda message: message.text == INFO_BUTTON, state=Admin.change_game_for_date,
    )
    dp.register_message_handler(change_game_settings, state=Admin.change_info)
    dp.register_message_handler(
        get_current_max_number, lambda message: message.text == MAX_PLAYERS_BUTTON, state=Admin.change_game_for_date,
    )
    dp.register_message_handler(change_max_number, state=Admin.max_number)
    dp.register_message_handler(reset_registration, lambda message: message.text == RESET_BUTTON, state=Admin.change_game_for_date)
    dp.register_message_handler(
        reset_registration_for_sure, lambda message: message.text == YES_BUTTON, state=Admin.reset,
    )
    dp.register_message_handler(no_reset_registration, lambda message: message.text == NO_BUTTON, state=Admin.reset)
    dp.register_message_handler(
        cancel_reset_registration, lambda message: message.text == CANCEL_BUTTON, state=Admin.players_for_date,
    )
    dp.register_message_handler(process_spy_button, lambda message: message.text == ADMIN_SPY_BUTTON, state=Admin.main)
    dp.register_message_handler(process_spy_start, lambda message: message.text == START_BUTTON, state=Admin.spy)
    dp.register_message_handler(
        process_return_admin, lambda message: message.text == CANCEL_BUTTON, state=Admin.spy_num_players,
    )
    dp.register_message_handler(process_spy_stop, lambda message: message.text == STOP_BUTTON, state=Admin.spy)
    dp.register_message_handler(process_spy_repeat, lambda message: message.text == REPEAT_BUTTON, state=Admin.spy)
    dp.register_message_handler(process_return_spy, lambda message: message.text == CANCEL_BUTTON, state=Admin.spy)
    dp.register_message_handler(process_spy_num_players, state=Admin.spy_num_players)
    dp.register_message_handler(
        create_game_for_date, lambda message: is_date_button(message.text), state=Admin.create_game,
    )
    dp.register_message_handler(change_game, lambda message: message.text == CHANGE_GAME_BUTTON, state=Admin.new_game)
    dp.register_message_handler(
        change_game_for_date,  state=Admin.change_game,
    )
    dp.register_message_handler(
        set_date_for_players, lambda message: is_date_button(message.text), state=Admin.players)

