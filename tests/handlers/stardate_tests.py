import datetime
import hmac

from config.settings import BLOG_ADDR, SECRET, confirm

from lamson.mail import MailRequest
from lamson.testing import RouterConversation, clear_queue, delivered, queue


client = RouterConversation("jim@localhost", "requests_tests")


class TestDeflection:
    def setUp(self):
        client.begin()


    def test_rejects_unexpected(self):
        """Reject unexpected messages."""

        client.say("random@localhost", "Unexpected messages should be dropped.")
        assert queue().count() == 0, "Responding to unexpected messages?!"


    def test_rejects_unexpected_confirms(self):
        """Reject unexpected confirmation messages."""

        client.say("punchit-confirm-abc123@localhost", "Unexpected confirmations should be dropped.")
        assert queue().count() == 0, "Accepting unexpected confirmation messages?!"


    def test_rejects_unauthorized_logs(self):
        """Reject unauthorized logs."""

        client.say("1900.01.01-abc123@localhost", "Unauthorized logs should be dropped.")
        assert queue().count() == 0, "Accepting unauthorized logs?!"


class TestDocking:
    def setUp(self):
        client.begin()


    def tearDown(self):
        confirm.storage.clear()


    def test_punching_it(self):
        """Get a confirmation message back upon subscription request."""

        c = client.say("punchit@localhost", "First message!",
                       expect="punchit-confirm-[a-z0-9]+@localhost")
        assert not delivered("First message!"), "The subscription message was re-sent early!"

        client.say(c['from'], "Let's go!",
                   expect="noreply@localhost")
        assert delivered("First message!"), "The subscription message wasn't re-sent!"


    def test_rejects_unauthorized_confirms(self):
        """Reject unauthorized confirmation messages."""

        c = client.say("punchit@localhost", "First message!",
                       expect="punchit-confirm-[a-z0-9]+@localhost")
        clear_queue()

        client.say("punchit-confirm-abc123@localhost", "Let's go!")
        assert queue().count() == 0, "Accepting unauthorized confirmation messages?!"


class TestTransmission:
    def setUp(self):
        client.begin()


    def confirm_subscription(self):
        """Confirm a subscription."""

        c = client.say("punchit@localhost", "First message!",
                       expect="punchit-confirm-[a-z0-9]+@localhost")
        client.say(c['from'], "Let's go!",
                   expect="noreply@localhost")
        clear_queue()


    def test_accepts_logs(self):
        """Accepts and forwards expected logs."""

        self.confirm_subscription()

        # Register an expected log.
        d = datetime.date.today()
        addr = "%s-%s@localhost" % (d.strftime('%Y.%m.%d'),
                                    hmac.new(SECRET, client.From).hexdigest())

        f = client.say(addr, "A log entry", expect=BLOG_ADDR)
        assert f['from'] == client.From and "A log entry" in f.body(), f


    def test_rejects_unexpected_logs(self):
        """Rejects unexpected logs."""

        self.confirm_subscription()

        client.say("1900.01.01-abc123@localhost", "Unexpected logs should be dropped.")
        assert queue().count() == 0, "Accepting unexpected logs?!"
