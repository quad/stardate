import sqlite3
import threading

from contextlib import nested

from lamson.confirm import ConfirmationStorage
from lamson.routing import StateStorage, ROUTE_FIRST_STATE


class SqliteConfirmationStorage(ConfirmationStorage):
    def __init__(self, database_path):
        self.lock = threading.RLock()
        self.connection = sqlite3.connect(database_path)

        with self.connection as conn:
            conn.execute('CREATE TABLE IF NOT EXISTS confirmations (key PRIMARY KEY, expected_secret NOT NULL, pending_message_id NOT NULL)')


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


class SqliteStateStorage(StateStorage):
    def __init__(self, database_path):
        self.lock = threading.RLock()
        self.connection = sqlite3.connect(database_path)

        with self.connection as conn:
            conn.execute('CREATE TABLE IF NOT EXISTS state (key PRIMARY KEY, state NOT NULL)')


    def key(self, key, sender):
        return repr((key, sender))


    def get(self, key, sender):
        with nested(self.lock, self.connection) as (lock, conn):
            c = conn.execute('SELECT state FROM state WHERE key=? LIMIT 1',
                             (self.key(key, sender),))
            v = c.fetchone()
            return v[0] if v else ROUTE_FIRST_STATE


    def set(self, key, sender, state):
        with nested(self.lock, self.connection) as (lock, conn):
            if state == ROUTE_FIRST_STATE:
                conn.execute('DELETE FROM state WHERE key=?', (self.key(key, sender),))
            else:
                conn.execute('INSERT OR REPLACE INTO state (key, state) VALUES (?, ?)',
                             (self.key(key, sender), state))


    def clear(self):
        with nested(self.lock, self.connection) as (lock, conn):
            conn.execute('DELETE FROM state')
