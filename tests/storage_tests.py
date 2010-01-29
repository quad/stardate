import threading

from collections import namedtuple
from Queue import Queue

from stardate.storage import _get_connection


def test_threaded_access():
    mock = namedtuple('Storage', 'database_path')(':memory:')
    db = _get_connection(mock)

    q = Queue()
    threading.Thread(target=lambda: q.put(_get_connection(mock))).start()

    assert db != q.get()
    assert db == _get_connection(mock)
