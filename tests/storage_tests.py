import datetime
import threading

from collections import namedtuple
from Queue import Queue

from config.test_storage import reminder_storage, state_storage

from stardate.storage import _get_connection


def test_threaded_access():
    def _get(path):
        with _get_connection(path) as c:
            return c

    mock = namedtuple('Storage', 'database_path')(':memory:')
    db = _get(mock)

    q = Queue()
    threading.Thread(target=lambda: q.put(_get(mock))).start()

    assert db != q.get()
    assert db == _get(mock)


class TestStellarCartography:
    def setUp(self):
        state_storage.clear()


    def test_no_addresses(self):
        assert state_storage.active_addresses() == []


    def test_finds_addresses(self):
        state_storage.set('stardate.handlers', 'spock@localhost', 'LOG')
        assert state_storage.active_addresses() == ['spock@localhost'], state_storage.active_addresses()


class TestGuinan:
    def setUp(self):
        reminder_storage.clear()


    def test_add(self):
        d = datetime.date.today()

        reminder_storage.set('spock@localhost', d)
        assert reminder_storage.get('spock@localhost') == d


    def test_clear(self):
        reminder_storage.set('spock@localhost', datetime.date.today())
        reminder_storage.clear()
        assert not reminder_storage.get('spock@localhost')
