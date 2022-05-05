import sqlite3
import time

"""
TABLES:
current_game: 
    telegram_id INTEGER
    nickname_lowered TEXT 
    create_time INTEGER
    nickname TEXT
    status INTEGER (0 - none, 1 - paid, 2 - new)
    
subscribers: 
    telegram_id INTEGER
    first_name TEXT
    last_name TEXT 
    username TEXT 
    create_time INTEGER 
    is_subscribed INTEGER
    
players
    telegram_id INTEGER
    nickname_lowered TEXT
    create_time INTEGER
    is_admin INTEGER
"""

class SQLighter:
    def __init__(self, database_file):
        """Connecting to DB and saving cursor"""
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def get_registered_players(self):
        with self.connection:
            rows = self.cursor.execute("SELECT nickname, status FROM current_game").fetchall()
            players = [r[0] for r in rows]
            status = [r[1] for r in rows]
            return players, status

    def count_registered_players(self):
        with self.connection:
            return self.cursor.execute("""SELECT count(*) FROM current_game""").fetchall()[0][0]

    def register_player(self, nickname, telegram_id=-1):
        with self.connection:
            return self.cursor.execute(f"""INSERT INTO current_game VALUES 
                                           ({telegram_id}, '{nickname.lower()}', {int(time.time())}, '{nickname}', 0)""")

    def unregister_player(self, telegram_id=None, nickname=None):
        assert telegram_id is not None or nickname is not None, "telegram_id or nickname must be passed"
        with self.connection:
            if telegram_id is None:
                return self.cursor.execute(f"DELETE FROM current_game WHERE nickname_lowered = '{nickname.lower()}'")
            else:
                return self.cursor.execute(f"DELETE FROM current_game WHERE telegram_id = {telegram_id}")

    def id_registered(self, telegram_id):
        with self.connection:
            result = self.cursor.execute(f"""SELECT EXISTS (SELECT * FROM current_game 
                                                          WHERE telegram_id = {telegram_id}) """).fetchall()[0][0]
            return bool(result)

    def nickname_registered(self, nickname):
        with self.connection:
            result = self.cursor.execute(f"""SELECT EXISTS (SELECT * FROM current_game 
                                              WHERE nickname_lowered = '{nickname.lower()}') """).fetchall()[0][0]
            return bool(result)

    def get_registered_nickname(self, telegram_id):
        with self.connection:
            return self.cursor.execute(f"""SELECT nickname FROM current_game WHERE telegram_id = {telegram_id}""").fetchall()[0][0]

    def clear(self):
        with self.connection:
            new_players = self.cursor.execute("""SELECT telegram_id, nickname_lowered FROM current_game
                                                 WHERE NOT EXISTS 
                                                     (SELECT 1 FROM players 
                                                      WHERE current_game.telegram_id = players.telegram_id
                                                          AND current_game.nickname_lowered = players.nickname_lowered)
                                                      AND current_game.telegram_id != -1
                                                      AND current_game.status != 0""").fetchall()
            for telegram_id, nickname_lowered in new_players:
                self.cursor.execute(f"""INSERT INTO players VALUES
                                        ({telegram_id}, '{nickname_lowered}', {int(time.time())}, 0)""")

            return self.cursor.execute("DELETE FROM current_game")

    def subscriber_exists(self, telegram_id):
        with self.connection:
            result = self.cursor.execute(f"""SELECT EXISTS (SELECT * FROM subscribers 
                                                          WHERE telegram_id = {telegram_id}) """).fetchall()[0][0]
            return bool(result)

    def add_subscriber(self, user):
        with self.connection:
            return self.cursor.execute(
                f"""INSERT INTO subscribers VALUES 
                ({user.id}, '{user.first_name}', '{user.last_name}', '{user.username}', {int(time.time())}, 1)"""
            )

    def get_subscribers(self):
        with self.connection:
            result = self.cursor.execute(f"""SELECT telegram_id FROM subscribers WHERE is_subscribed = 1""")
            return [i[0] for i in result]

    def get_subscribers_rows(self):
        with self.connection:
            result = self.cursor.execute(
                f"SELECT first_name, last_name, username, create_time FROM subscribers WHERE is_subscribed = 1"
            ).fetchall()
            return result

    def get_all_players_nicks(self):
        with self.connection:
            result = self.cursor.execute(f"SELECT nickname_lowered FROM players").fetchall()
            return [i[0] for i in result]

    def get_all_players_ids(self):
        with self.connection:
            result = self.cursor.execute(f"SELECT telegram_id FROM players").fetchall()
            return [i[0] for i in result]

    def change_payment_state(self, nickname):
        with self.connection:
            status = self.cursor.execute(
                f"SELECT status FROM current_game WHERE nickname = '{nickname}'"
            ).fetchall()[0][0]
            new_status = (not status) * 1
            self.cursor.execute(
                f"""UPDATE current_game SET status = {new_status} WHERE nickname = '{nickname}'"""
            )

    def change_newby_state(self, nickname):
        with self.connection:
            status = self.cursor.execute(
                f"SELECT status FROM current_game WHERE nickname = '{nickname}'"
            ).fetchall()[0][0]
            new_status = (not status) * 2
            self.cursor.execute(
                f"""UPDATE current_game SET status = {new_status} WHERE nickname = '{nickname}'"""
            )

    def close(self):
        self.connection.close()
