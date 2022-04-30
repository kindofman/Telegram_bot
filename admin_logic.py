from datetime import datetime
from init import (
    dp,
    Form,
    db,
    bot,
)
from buttons import *


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


@dp.message_handler(lambda message: message.text == CANCEL_BUTTON, state=[Form.mailing, Form.mailing_all])
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
