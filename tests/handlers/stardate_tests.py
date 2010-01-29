from config.settings import BLOG_ADDR, confirm

from lamson.mail import MailRequest
from lamson.testing import RouterConversation, clear_queue, delivered, queue


client = RouterConversation("jim@localhost", "requests_tests")


def test_rejects_unexpected():
    """Reject unexpected messages."""

    client.begin()
    client.say("random@localhost", "Unexpected messages should be dropped.")
    assert queue().count() == 0, "Responding to unexpecte messages?!"


def test_punching_it():
    """Get a confirmation message back upon subscription request."""

    client.begin()
    confirm = client.say("punchit@localhost", "First message!",
                         expect="punchit-confirm-[a-z0-9]+@localhost")
    assert not delivered("First message!"), "The subscription message was re-sent early!"

    client.say(confirm['from'], "Let's go!",
               expect="noreply@localhost")
    assert delivered("First message!"), "The subscription message wasn't re-sent!"


def test_rejects_unexpected_confirms():
    """Reject unexpected confirmation messages."""

    client.begin()
    client.say("punchit-confirm-abc123@localhost", "Unexpected confirmations should be dropped.")
    assert queue().count() == 0, "Accepting random confirmation messages?!"


def test_rejects_unauthorized_logs():
    """Reject unauthorized logs."""

    client.begin()
    client.say("1900.01.01-confirm-abc123@localhost", "Unauthorized logs should be dropped.")
    assert queue().count() == 0, "Accepting unauthorized logs?!"


def confirm_subscription(client):
    """Confirm a subscription."""

    client.begin()
    c = client.say("punchit@localhost", "First message!",
                   expect="punchit-confirm-[a-z0-9]+@localhost")
    client.say(c['from'], "Let's go!",
               expect="noreply@localhost")
    clear_queue()


def test_accepts_logs():
    """Accepts and forwards expected logs."""

    confirm_subscription(client)

    target = '1900.01.01'

    # Register an expected log.
    m = MailRequest('localhost', client.From, target + '@localhost', '')
    addr = confirm.register(target, m)

    f = client.say(addr + '@localhost', "A log entry", expect=BLOG_ADDR)
    assert f['from'] == client.From and "A log entry" in f.body(), f


def test_rejects_unexpected_logs():
    """Rejects unexpected logs."""

    confirm_subscription(client)

    client.say("1900.01.01-confirm-abc123@localhost", "Unexpected logs should be dropped.")
    assert queue().count() == 0, "Accepting unexpected logs?!"
