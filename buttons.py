from aiogram import types


REGISTRATION_BUTTON = "Регистрация 📝️‍‍‍"
NEAREST_GAME_BUTTON = "Ближайшие встречи 📆"
RULES_BUTTON = "Правила игры 👩🏻‍⚖️"
GESTURES_BUTTON = "Игровые жесты 👌🏼"
CANCEL_BUTTON = "Назад 🙅🏼"
YES_BUTTON = "Да ✅"
NO_BUTTON = "Нет ❌"
ADD_PLAYER_BUTTON = "Добавить‍"
REMOVE_PLAYER_BUTTON = "Убрать"
EXIT_ADMIN_BUTTON = "Выйти из админских кнопок ✈️"
VIEW_PLAYERS_BUTTON = "Список игроков"
MAILING_ALL_BUTTON = "Рассылка всем"
MAFIA_BUTTON = "Мафия 🕵🏻"
PLAYER_SPY_BUTTON = "Шпион 👀"
VOTE_BUTTON = "Голосование 🙋🏻"
BOARD_GAMES_BUTTON = "Настолки 🎲"
PAYMENT_VERIFIED_BUTTON = "Оплачено?"
NEWBY_STATE_BUTTON = "Новый игрок"
NEW_GAME_BUTTON = "Новая игра"
CREATE_GAME_BUTTON = "Создать игру"
CHANGE_GAME_BUTTON = "Изменить игру"
PLAYERS_BUTTON = "Регистрация"
ADMIN_MAFIA_BUTTON = "Мафия"
ADMIN_SPY_BUTTON = "Шпион"
INFO_BUTTON = "Инфо"
MAX_PLAYERS_BUTTON = "Кол-во игроков"
RESET_BUTTON = "Удалить игру"
START_BUTTON = "Старт"
STOP_BUTTON = "Стоп"
REPEAT_BUTTON = "Повторить раздачу"
GET_CARD_BUTTON = "Получить карту"


base_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
base_markup.add(NEAREST_GAME_BUTTON)
base_markup.row(MAFIA_BUTTON, BOARD_GAMES_BUTTON)

nearest_game_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
nearest_game_markup.row(REGISTRATION_BUTTON, CANCEL_BUTTON)

mafia_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
mafia_markup.row(RULES_BUTTON, GESTURES_BUTTON)
mafia_markup.row(VOTE_BUTTON, CANCEL_BUTTON)

board_games_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
board_games_markup.add(PLAYER_SPY_BUTTON)
board_games_markup.add(CANCEL_BUTTON)

player_spy_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
player_spy_markup.row(GET_CARD_BUTTON, CANCEL_BUTTON)

cancel_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
cancel_markup.add(CANCEL_BUTTON)

yes_no_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
yes_no_markup.add(YES_BUTTON, NO_BUTTON)

admin_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
admin_markup.row(NEW_GAME_BUTTON, PLAYERS_BUTTON)
admin_markup.row(ADMIN_MAFIA_BUTTON, ADMIN_SPY_BUTTON)
admin_markup.add(EXIT_ADMIN_BUTTON)

new_game_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
new_game_markup.row(CREATE_GAME_BUTTON)
new_game_markup.row(CHANGE_GAME_BUTTON)
new_game_markup.row(CANCEL_BUTTON)

change_game_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
change_game_markup.row(INFO_BUTTON, MAX_PLAYERS_BUTTON)
change_game_markup.row(RESET_BUTTON, CANCEL_BUTTON)

players_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
players_markup.row(ADD_PLAYER_BUTTON, REMOVE_PLAYER_BUTTON)
players_markup.row(PAYMENT_VERIFIED_BUTTON, NEWBY_STATE_BUTTON)
players_markup.add(CANCEL_BUTTON)

admin_spy_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
admin_spy_markup.row(START_BUTTON, STOP_BUTTON)
admin_spy_markup.add(REPEAT_BUTTON, CANCEL_BUTTON)



