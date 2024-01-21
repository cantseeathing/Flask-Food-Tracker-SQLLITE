import sqlite3
from flask import g

DATABASE = 'food_tracker.db'


class Helper:
    def __init__(self):
        self.db = self.get_db()

    @staticmethod
    def get_db():
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
        return db
