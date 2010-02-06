import datetime

from lamson.testing import RouterConversation, clear_queue, delivered, queue

from config.test_storage import reminder_storage, state_storage
from stardate.handlers import engage


client = RouterConversation("jim@localhost", "requests_tests")


def test_inertial_dampener():
    reminder_storage.clear()
    state_storage.clear()

    client.begin()

    engage()
    assert queue().count() == 0, "Reminding when there's no one to remind?"


class TestGoingToWarp:
    def setUp(self):
        reminder_storage.clear()
        state_storage.clear()

        client.begin()


    def test_first_posting(self):
        state_storage.set('stardate.handlers', 'spock@localhost', 'LOG')

        engage()
        assert delivered("Captain's Log"), "No reminder log delivered."


    def test_no_double_opening_posting(self):
        state_storage.set('stardate.handlers', 'spock@localhost', 'LOG')

        engage()
        clear_queue()

        engage()
        assert queue().count() == 0, "Delivered a duplicate reminder after promotion."


    def test_backqueued_postings(self):
        state_storage.set('stardate.handlers', 'spock@localhost', 'LOG')
        reminder_storage.set('spock@localhost', datetime.date.today() - datetime.timedelta(days=5))

        engage()
        assert delivered("Captain's Log"), "No reminder log delivered."
        assert queue().count() == 5, "%u backqueued reminders were delivered?" % queue().count()


    def test_no_double_backqueued_postings(self):
        state_storage.set('stardate.handlers', 'spock@localhost', 'LOG')
        reminder_storage.set('spock@localhost', datetime.date.today() - datetime.timedelta(days=5))

        engage()
        clear_queue()

        engage()
        assert queue().count() == 0, "Delivered a duplicate reminder after the backqueue."
