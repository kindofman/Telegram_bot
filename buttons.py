from aiogram import types


REGISTRATION_BUTTON = "Зарегистрироваться"
INFO_BUTTON = "Информация по игре"
NEAREST_GAME_BUTTON = "Ближайшая игра"
RULES_BUTTON = "Правила игры"
GESTURES_BUTTON = "Игровые жесты"
CANCEL_BUTTON = "Отмена ↩"
YES_BUTTON = "Да"
NO_BUTTON = "Нет"

base_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
base_markup.add(REGISTRATION_BUTTON)
base_markup.add(INFO_BUTTON)

info_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
info_markup.add(NEAREST_GAME_BUTTON)
info_markup.add(RULES_BUTTON)
info_markup.add(GESTURES_BUTTON)

yes_no_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
yes_no_markup.add(YES_BUTTON, NO_BUTTON)

cancel_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, one_time_keyboard=False)
cancel_markup.add(CANCEL_BUTTON)
