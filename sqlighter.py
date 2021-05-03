import sqlite3
import time

class SQLighter:
    def __init__(self, database_file):
        """Connecting to DB and saving cursor"""
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def get_registered_players(self):
        with self.connection:
            rows = self.cursor.execute("SELECT nickname FROM current_game").fetchall()
            return [r[0] for r in rows]

    def count_registered_players(self):
        with self.connection:
            return self.cursor.execute("""SELECT count(*) FROM current_game""").fetchall()[0][0]

    def register_player(self, nickname, telegram_id=-1):
        with self.connection:
            return self.cursor.execute(f"""INSERT INTO current_game VALUES 
                                           ({telegram_id}, '{nickname.lower()}', {int(time.time())}, '{nickname}')""")

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
                                                      AND current_game.telegram_id != -1""").fetchall()
            for telegram_id, nickname_lowered in new_players:
                self.cursor.execute(f"""INSERT INTO players VALUES
                                        ({telegram_id}, '{nickname_lowered}', {int(time.time())}, 0)""")

            return self.cursor.execute("DELETE FROM current_game")

    def close(self):
        self.connection.close()
