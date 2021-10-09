from aiogram import types


REGISTRATION_BUTTON = "Регистрация 📝️‍‍‍"
INFO_BUTTON = "Об игре 🕵🏻‍♂️"
NEAREST_GAME_BUTTON = "Ближайшая игра 📆"
RULES_BUTTON = "Правила игры 👩🏻‍⚖️"
GESTURES_BUTTON = "Игровые жесты 👌"
CANCEL_BUTTON = "Отмена 🙅🏼"
YES_BUTTON = "Да ✅"
NO_BUTTON = "Нет ❌"
SUBSCRIBE_BUTTON = "Подписаться на рассылку 🔔"
MAILING_BUTTON = "Рассылка 📩"
ADD_PLAYER_BUTTON = "Добавить игрока 👩‍👦"
REMOVE_PLAYER_BUTTON = "Убрать игрока 🏃‍♂️"
EXIT_ADMIN_BUTTON = "Выйти из админских кнопок ✈️"


base_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
base_markup.row(REGISTRATION_BUTTON, INFO_BUTTON)
base_markup.add(SUBSCRIBE_BUTTON)

info_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
info_markup.add(NEAREST_GAME_BUTTON)
info_markup.row(RULES_BUTTON, GESTURES_BUTTON)

yes_no_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
yes_no_markup.add(YES_BUTTON, NO_BUTTON)

cancel_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
cancel_markup.add(CANCEL_BUTTON)

admin_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
admin_markup.add(MAILING_BUTTON)
admin_markup.row(ADD_PLAYER_BUTTON, REMOVE_PLAYER_BUTTON)
admin_markup.add(EXIT_ADMIN_BUTTON)
