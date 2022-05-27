from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2


import argparse
from sqlighter import SQLighter
import config
import logging
from aioredis import Redis


parser = argparse.ArgumentParser(description='Mafia bot')
parser.add_argument("purpose", help="Mode", default="test", choices={"test", "prod"}, nargs="?")
args = parser.parse_args()

API_TOKEN = config.API_TOKEN_TEST if args.purpose == "test" else config.API_TOKEN_PROD

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = RedisStorage2()
redis = Redis()
dp = Dispatcher(bot, storage=storage)
db = SQLighter("files/database.db")
