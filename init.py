from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import argparse
from sqlighter import SQLighter
import config
import logging


# States
class Form(StatesGroup):
    start = State()
    nickname = State()  # Will be represented in storage as 'Form:nickname'
    unregister = State()
    nearest_game = State()
    mafia = State()
    change_info = State()
    max_number = State()
    reset = State()
    register_player = State()
    admin = State()
    # mailing = State()
    # print_players = State()
    # mailing_all = State()
    new_game = State()
    players = State()


parser = argparse.ArgumentParser(description='Mafia bot')
parser.add_argument("purpose", help="Mode", default="test", choices={"test", "prod"}, nargs="?")
args = parser.parse_args()

API_TOKEN = config.API_TOKEN_TEST if args.purpose == "test" else config.API_TOKEN_PROD

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = SQLighter("files/database.db")
