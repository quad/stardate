import datetime
import logging
import random

from pkg_resources import resource_stream

from lamson import view
from lamson.routing import route

from config.settings import BLOG_ADDR, relay, confirm


WELCOME_QUOTES = [l.strip()
                  for l in resource_stream(__name__, 'data/welcome_quotes.txt')]
CONFIRM_QUOTES = [l.strip()
                  for l in resource_stream(__name__, 'data/confirm_quotes.txt')]


@route('punchit@(host)')
def START(message, host):
    quotes = WELCOME_QUOTES
    confirm.send(relay, 'punchit', message, 'start_confirm.msg', locals())

    return CONFIRMING


@route('punchit-confirm-(id_number)@(host)', id_number='[a-z0-9]+')
def CONFIRMING(message, id_number, host):
    original = confirm.verify('punchit', message['from'], id_number)

    if original:
        original['to'] = BLOG_ADDR
        relay.deliver(original)

        welcome = view.respond(locals(),
                               'welcome.msg',
                               From='noreply@%(host)s',
                               To=message['from'],
                               Subject=random.choice(CONFIRM_QUOTES))
        relay.deliver(welcome)

        logging.info("Confirmed %s", message['from'])

        return LOG
    else:
        logging.warning("Invalid confirm from %s", message['from'])

        return CONFIRMING


@route("(date)\+(id_number)@(host)", date='\d{4}\.\d{2}\.\d{2}', id_number='[a-z0-9]+')
def LOG(message, date, id_number, host):
    d = datetime.datetime.strptime(date, '%Y.%m.%d')

    if d > datetime.datetime.now():
        logging.warning("Space-time anomaly detected around %s.", message['from'])
    # TODO: Check the id_number validity.
    else:
        logging.debug("Captain's Log from %s on date: %s", message['from'], message['date'])

    # Appropriately date the entry.
    message['date'] = d.strftime('%a, %d %b %Y %H:%M:%S +0000')
    message['to'] = BLOG_ADDR

    relay.deliver(message)

    return LOG
