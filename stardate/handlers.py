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


@route("(date)-confirm-(id_number)@(host)", date='\d{4}\.\d{2}\.\d{2}', id_number='[a-z0-9]+')
def LOG(message, date, id_number, host):
    notification = confirm.verify(date, message['from'], id_number)

    if notification:
        d = datetime.datetime.strptime(date, '%Y.%m.%d')

        message['date'] = d.strftime('%a, %d %b %Y %H:%M:%S +0000')
        message['to'] = BLOG_ADDR

        relay.deliver(message)

        logging.info("%s's Log, supplemental. Stardate: %s", message['from'], d)
    else:
        logging.warning("Transphasic shields holding under assault from %s", message['from'])

    return LOG
