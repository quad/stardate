import threading

from collections import namedtuple
from Queue import Queue

from config.test_storage import state_storage

from stardate.storage import _get_connection


def test_threaded_access():
    mock = namedtuple('Storage', 'database_path')(':memory:')
    db = _get_connection(mock)

    q = Queue()
    threading.Thread(target=lambda: q.put(_get_connection(mock))).start()

    assert db != q.get()
    assert db == _get_connection(mock)
    

class TestStellarCartography:
    def setUp(self):
        state_storage.clear()


    def test_no_addresses(self):
        assert state_storage.active_addresses() == []


    def test_finds_addresses(self):
        state_storage.set('stardate.handlers', 'spock@localhost', 'LOG')
        assert state_storage.active_addresses() == ['spock@localhost'], state_storage.active_addresses()
