from aiogram import types


REGISTRATION_BUTTON = "Регистрация 📝️‍‍‍"
NEAREST_GAME_BUTTON = "Ближайшая встреча 📆"
RULES_BUTTON = "Правила игры 👩🏻‍⚖️"
GESTURES_BUTTON = "Игровые жесты 👌🏼"
CANCEL_BUTTON = "Назад 🙅🏼"
YES_BUTTON = "Да ✅"
NO_BUTTON = "Нет ❌"
MAILING_BUTTON = "Рассылка"
VIEW_SUBSCRIBERS_BUTTON = "Кто подписался?"
ADD_PLAYER_BUTTON = "Добавить игрока‍"
REMOVE_PLAYER_BUTTON = "Убрать игрока"
EXIT_ADMIN_BUTTON = "Выйти из админских кнопок ✈️"
VIEW_PLAYERS_BUTTON = "Список игроков"
MAILING_ALL_BUTTON = "Рассылка всем"
MAFIA_BUTTON = "Мафия 🕵🏻"
SPY_BUTTON = "Шпион 👀"
VOTE_BUTTON = "Голосование 🙋🏻"
BOARD_GAMES_BUTTON = "Настолки 🎲"


base_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
base_markup.add(NEAREST_GAME_BUTTON)
base_markup.row(MAFIA_BUTTON, BOARD_GAMES_BUTTON)

nearest_game_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
nearest_game_markup.row(REGISTRATION_BUTTON, CANCEL_BUTTON)

mafia_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
mafia_markup.row(RULES_BUTTON, GESTURES_BUTTON)
mafia_markup.row(VOTE_BUTTON, CANCEL_BUTTON)

cancel_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
cancel_markup.add(CANCEL_BUTTON)

yes_no_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
yes_no_markup.add(YES_BUTTON, NO_BUTTON)

admin_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
# admin_markup.row(MAILING_BUTTON, VIEW_SUBSCRIBERS_BUTTON)
# admin_markup.row(VIEW_PLAYERS_BUTTON, MAILING_ALL_BUTTON)
admin_markup.add(MAILING_ALL_BUTTON)
admin_markup.row(ADD_PLAYER_BUTTON, REMOVE_PLAYER_BUTTON)
admin_markup.add(EXIT_ADMIN_BUTTON)

# info_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
# info_markup.add(NEAREST_GAME_BUTTON)
# info_markup.row(RULES_BUTTON, GESTURES_BUTTON)



