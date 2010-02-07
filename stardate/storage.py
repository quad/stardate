from __future__ import with_statement

import datetime
import logging
import sqlite3
import threading

from contextlib import contextmanager

import lamson.confirm
import lamson.routing

from lamson.routing import ROUTE_FIRST_STATE


_connection_locks = {}
_connection_pool = threading.local()
_connection_pool.dbs = {}

@contextmanager
def _get_connection(self):
    if not hasattr(_connection_pool, 'dbs'):
        _connection_pool.dbs = {}

        # WARNING: sqlite3 lacks concurrency support for in-memory databases.
        # If you need that, use the lamson default stack instead.

        if self.database_path == ':memory:':
            logging.warning('Multithreaded access on an in-memory sqlite database.')

    with _connection_locks.setdefault(self.database_path, threading.RLock()):
        conn = _connection_pool.dbs.setdefault(
            self.database_path,
            sqlite3.connect(self.database_path))

        try:
            yield conn
            conn.commit()
        except:
            conn.rollback()
            raise


class ConfirmationStorage(lamson.confirm.ConfirmationStorage):
    SQL_CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS
            confirmations (
                target NOT NULL,
                from_address NOT NULL,
                expected_secret NOT NULL,
                pending_message_id NOT NULL,
                PRIMARY KEY (target, from_address)
            )
    """
    connection = property(_get_connection)


    def __init__(self, database_path):
        self.database_path = database_path
        self.lock = threading.RLock()

        with self.connection as conn:
            conn.execute(self.SQL_CREATE_TABLE)


    def clear(self):
        with self.connection as conn:
            conn.execute('DELETE FROM confirmations')


    def get(self, target, from_address):
        with self.connection as conn:
            c = conn.execute(
                'SELECT expected_secret, pending_message_id FROM confirmations'
                ' WHERE target=? AND from_address=? LIMIT 1',
                (target, from_address))
            return c.fetchone() or (None, None)


    def delete(self, target, from_address):
        with self.connection as conn:
            conn.execute(
                'DELETE FROM confirmations WHERE target=? AND from_address=?',
                (target, from_address))


    def store(self, target, from_address, expected_secret, pending_message_id):
        with self.connection as conn:
            conn.execute(
                'INSERT OR REPLACE INTO confirmations'
                ' (target, from_address, expected_secret, pending_message_id)'
                ' VALUES (?, ?, ?, ?)',
                (target, from_address, expected_secret, pending_message_id))


class ReminderDatesStorage:
    SQL_CREATE_TABLE = """CREATE TABLE IF NOT EXISTS
        reminders (
            address PRIMARY KEY,
            year NOT NULL,
            month NOT NULL,
            day NOT NULL
        )"""
    connection = property(_get_connection)


    def __init__(self, database_path):
        self.database_path = database_path
        self.lock = threading.RLock()

        with self.connection as conn:
            conn.execute(self.SQL_CREATE_TABLE)


    def get(self, address):
        with self.connection as conn:
            d = conn.execute('SELECT year, month, day FROM reminders'
                             ' WHERE address=? LIMIT 1', (address,)).fetchone()

            return datetime.date(*d) if d else None


    def set(self, address, date):
        with self.connection as conn:
            d = conn.execute(
                'INSERT OR REPLACE INTO reminders (address, year, month, day)'
                ' VALUES (?, ?, ?, ?)',
                (address, date.year, date.month, date.day))


    def clear(self):
        with self.connection as conn:
            conn.execute('DELETE FROM reminders')


class StateStorage(lamson.routing.StateStorage):
    SQL_CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS
            state (
                key NOT NULL,
                sender NOT NULL,
                state NOT NULL,
                PRIMARY KEY (key, sender)
            )
    """
    connection = property(_get_connection)


    def __init__(self, database_path):
        self.database_path = database_path
        self.lock = threading.RLock()

        with self.connection as conn:
            conn.execute(self.SQL_CREATE_TABLE)


    def get(self, key, sender):
        with self.connection as conn:
            c = conn.execute('SELECT state FROM state WHERE key=? AND sender=? LIMIT 1',
                             (key, sender))
            v = c.fetchone()
            return v[0] if v else ROUTE_FIRST_STATE


    def set(self, key, sender, state):
        with self.connection as conn:
            if state == ROUTE_FIRST_STATE:
                conn.execute('DELETE FROM state WHERE key=? AND sender=?', (key, sender))
            else:
                conn.execute('INSERT OR REPLACE INTO state (key, sender, state) VALUES (?, ?, ?)',
                             (key, sender, state))


    def clear(self):
        with self.connection as conn:
            conn.execute('DELETE FROM state')


    def active_addresses(self):
        with self.connection as conn:
            addrs = conn.execute('SELECT sender FROM state WHERE key=? AND state=?',
                                 ('stardate.handlers', 'LOG'))

        return [addr for addr, in addrs.fetchall()] or []
