import random
from aiogram import Bot
import os

from loader import redis


"""
Соотношение игроки/шпионы
До 8 игроков - 1 шпион
9-14 игроков - 2 шпиона
15 и больше - 3 шпиона

Старт:
    - случайно выбирается локация
    - готовятся карты для введенного кол-ва участников с перемешиванием

Получить карту:
    - регистрация пользователя в таблице

Как хранить состояние карт?
    - число шпионов
    - массив нулей и единиц
    - таблица сиквел

Зачем нужно дожидаться входа всех игроков?
    - чтобы случайно не дать больше шпионов, чем предусмотрено.

Как узнать, что все игроки нажали "получить карту?"
    - после каждого нажатия проверять, сколько человек нажали
    - Ная может нажимать проверить, сколько человек нажали на кнопку
"""

LOCATIONS_REDIS = "locations_"
PLAYERS_NUM = "players_num"

SPY_FOLDER = "spy"
LOCATIONS_FOLDER = "locations"
FILES_FOLDER = "files"
PATH_TO_LOCATIONS = os.path.join(FILES_FOLDER, SPY_FOLDER, LOCATIONS_FOLDER)
PATH_TO_SPY = os.path.join(FILES_FOLDER, SPY_FOLDER, "spy.jpg")


def make_roles(players_num: int):
    spies = [1]
    if players_num >= 9:
        spies.append(1)
    if players_num >= 15:
        spies.append(1)
    return spies + [0] * (players_num - len(spies))

async def get_location_path():
    location = await redis.rpop(LOCATIONS_REDIS)
    if location is None:
        locations = os.listdir(PATH_TO_LOCATIONS)
        random.shuffle(locations)
        await redis.rpush(LOCATIONS_REDIS, *locations)
        location = await redis.rpop(LOCATIONS_REDIS)
    location = location.decode()
    return os.path.join(FILES_FOLDER, SPY_FOLDER, LOCATIONS_FOLDER, location)

async def deal_cards(players: list, players_num: int, bot: Bot):
    roles = make_roles(players_num)
    random.shuffle(roles)
    location_path = await get_location_path()
    for p, r in zip(players, roles):
        if r == 0:
            await bot.send_photo(p, open(location_path, 'rb'))
        else:
            await bot.send_photo(p, open(PATH_TO_SPY, 'rb'))


