from lamson.testing import RouterConversation, queue


client = RouterConversation("somedude@localhost", "requests_tests")


def test_rejects_unexpected():
    """
    Reject unexpected messages.
    """

    client.begin()
    client.say("random@localhost", "Unexpected messages should be dropped.")


class TestGoingToWarp:
    pass


class TestAyeAye:
    def test_rejects_unexpected_confirms(self):
        """
        Reject unexpected confirmation messages.
        """

        client.begin()
        client.say("punchit-confirm-abc123@localhost", "Unexpected confirmations should be dropped.")
        assert queue().count() == 0, "Accepting random confirmation messages?!"


class TestCaptainsLog:
    def test_rejects_unexpected_logs(self):
        """
        Reject unexpected logs.
        """

        client.begin()
        client.say("0000.00.00-abc123@localhost", "Unexpected logs should be dropped.")
        assert queue().count() == 0, "Accepting random logs messages?!"
