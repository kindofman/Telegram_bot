from loader import redis

import json
from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass
from common.utils import date_to_info


class Game:
    players = "players"
    info = "info"
    status = "status"
    max_players = "max_players"
    default_max_players = 14
    default_status = 0


class RedisField:
    games = "games"


class Status(Enum):
    unknown = 0
    paid = 1
    new = 2


@dataclass
class Person:
    id: int
    nick: str
    status: Status


def encode_status(obj):
    if isinstance(obj, Status):
        return {"__status__": True, "value": obj.value}
    elif isinstance(obj, Person):
        return {"__person__": True, "id": obj.id, "nick": obj.nick, "status": obj.status}

def decode_status(obj):
    if "__status__" in obj:
        return Status(obj["value"])
    if "__person__" in obj:
        return Person(obj["id"], obj["nick"], obj["status"])
    return obj


async def load_games():
    games = await redis.get(RedisField.games)
    if games is None:
        return dict()
    return json.loads(games, object_hook=decode_status)


async def dump_games(games):
    await redis.set(RedisField.games, json.dumps(games, default=encode_status))


async def _add_player(date, telegram_id: int, nick: str, status: Status):
    games = await load_games()
    games[date][Game.players].append(Person(
        id = telegram_id, nick = nick, status = status
    ))
    await dump_games(games)


async def create_game(date: str):
    base_info = date_to_info(date)
    games = await load_games()
    games[date] = {Game.players: [], Game.info: base_info, Game.max_players: Game.default_max_players}
    await dump_games(games)


async def delete_game(date: str):
    games = await load_games()
    del games[date]
    await dump_games(games)


async def get_all_games() -> List[str]:
    games = await load_games()
    return list(games)


async def get_game(date: str) -> Optional[Dict]:
    games = await load_games()
    if date in games:
        return games[date]
    return None


async def add_player_by_nick(date: str, nick: str):
    await _add_player(date, telegram_id=-1, nick=nick, status=Status.unknown)


async def add_player_by_id(date: str, telegram_id: int, nick: str):
    await _add_player(date, telegram_id=telegram_id, nick=nick, status=Status.unknown)


async def remove_player_by_id(date: str, telegram_id: int):
    games = await load_games()
    games[date][Game.players] = [p for p in games[date][Game.players] if p.id != telegram_id]
    await dump_games(games)


async def remove_player_by_nick(date: str, nick: str):
    games = await load_games()
    games[date][Game.players] = [p for p in games[date][Game.players] if p.nick.lower() != nick.lower()]
    await dump_games(games)


async def player_exists_by_id(date: str, telegram_id: int) -> bool:
    games = await load_games()
    return any(telegram_id == p.id for p in games[date][Game.players])


async def player_exists_by_nick(date: str, nick: str):
    games = await load_games()
    return any(nick.lower() == p.nick.lower() for p in games[date][Game.players])


async def get_registered_players(date: str) -> List[Person]:
    games = await load_games()
    return games[date][Game.players]


async def count_registered_players(date: str) -> int:
    games = await load_games()
    return games[date][Game.players].__len__()


async def get_nickname(date: str, telegram_id: int):
    games = await load_games()
    player = next((p for p in games[date][Game.players] if p.id == telegram_id))
    return player.nick


async def remove_game(date: str):
    games = await load_games()
    del games[date]
    await dump_games(games)


async def change_max_players(date: str, new_max_players: int):
    games = await load_games()
    games[date][Game.max_players] = new_max_players
    await dump_games(games)


async def get_max_players(date: str) -> int:
    games = await load_games()
    return games[date][Game.max_players]


async def change_info(date: str, new_info: str):
    games = await load_games()
    games[date][Game.info] = new_info
    await dump_games(games)


async def get_info(date: str) -> str:
    games = await load_games()
    return games[date][Game.info]


async def change_newby_state(date: str, nick: str):
    games = await load_games()
    for player in games[date][Game.players]:
        if player.nick == nick:
            player.status = Status((not player.status.value) * 2)
    await dump_games(games)


async def change_payment_state(date: str, nick: str):
    games = await load_games()
    for player in games[date][Game.players]:
        if player.nick == nick:
            player.status = Status(not player.status.value)
    await dump_games(games)




