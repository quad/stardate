from nose.tools import *

from lamson.testing import *


client = RouterConversation("somedude@localhost", "requests_tests")


def test_drops_open_relay_messages():
    """
    Make sure that mail NOT for us gets dropped silently.
    """

    client.begin()
    client.say("tester@badplace.notinterwebs", "Relay should not happen")
    assert queue().count() == 0, "You are configured currently to accept everything.  You should change config/settings.py router_defaults so host is your actual host name that will receive mail."
