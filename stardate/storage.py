import sqlite3
import threading

from contextlib import nested

import lamson.confirm
import lamson.routing

from lamson.routing import ROUTE_FIRST_STATE


# WARNING: There's no way to pass an in-memory sqlite database between threads.
# Use the lamson default stack if you need that.


class ConfirmationStorage(lamson.confirm.ConfirmationStorage):
    SQL_CREATE_TABLE = """CREATE TABLE IF NOT EXISTS
        confirmations (
            key PRIMARY KEY,
            expected_secret NOT NULL,
            pending_message_id NOT NULL)"""


    def __init__(self, database_path):
        self.database_path = database_path
        self.db = threading.local()
        self.lock = threading.RLock()

        with self.connection as conn:
            conn.execute(self.SQL_CREATE_TABLE)


    @property
    def connection(self):
        if not hasattr(self.db, 'connection'):
            self.db.connection = sqlite3.connect(self.database_path)

        return self.db.connection


    def clear(self):
        with nested(self.lock, self.connection) as (lock, conn):
            conn.execute('DELETE FROM confirmations')


    def get(self, target, from_address):
        with nested(self.lock, self.connection) as (lock, conn):
            c = conn.execute('SELECT expected_secret, pending_message_id FROM confirmations WHERE key=? LIMIT 1',
                             (self.key(target, from_address),))
            return c.fetchone() or (None, None)


    def delete(self, target, from_address):
        with nested(self.lock, self.connection) as (lock, conn):
            conn.execute('DELETE FROM confirmations WHERE key=?',
                         (self.key(target, from_address),))


    def store(self, target, from_address, expected_secret, pending_message_id):
        with nested(self.lock, self.connection) as (lock, conn):
            conn.execute('INSERT OR REPLACE INTO confirmations (key, expected_secret, pending_message_id) VALUES (?, ?, ?)',
                         (self.key(target, from_address), expected_secret, pending_message_id))


class StateStorage(lamson.routing.StateStorage):
    SQL_CREATE_TABLE = """CREATE TABLE IF NOT EXISTS
        state (
            key NOT NULL,
            sender NOT NULL,
            state NOT NULL)"""


    def __init__(self, database_path):
        self.database_path = database_path
        self.db = threading.local()
        self.lock = threading.RLock()

        with self.connection as conn:
            conn.execute(self.SQL_CREATE_TABLE)


    @property
    def connection(self):
        if not hasattr(self.db, 'connection'):
            self.db.connection = sqlite3.connect(self.database_path)

        return self.db.connection


    def get(self, key, sender):
        with nested(self.lock, self.connection) as (lock, conn):
            c = conn.execute('SELECT state FROM state WHERE key=? AND sender=? LIMIT 1',
                             (key, sender))
            v = c.fetchone()
            return v[0] if v else ROUTE_FIRST_STATE


    def set(self, key, sender, state):
        with nested(self.lock, self.connection) as (lock, conn):
            conn.execute('DELETE FROM state WHERE key=? AND sender=?', (key, sender))

            if state != ROUTE_FIRST_STATE:
                conn.execute('INSERT INTO state (key, sender, state) VALUES (?, ?, ?)',
                             (key, sender, state))


    def clear(self):
        with nested(self.lock, self.connection) as (lock, conn):
            conn.execute('DELETE FROM state')
