import datetime
import hmac
import logging
import random

from pkg_resources import resource_stream

from lamson import view
from lamson.routing import route

from config.settings import BLOG_ADDR, FROM_HOST, SECRET, relay, confirm, \
        scheduler, storage


WELCOME_QUOTES = [l.strip()
                  for l in resource_stream(__name__, 'data/welcome_quotes.txt')]
CONFIRM_QUOTES = [l.strip()
                  for l in resource_stream(__name__, 'data/confirm_quotes.txt')]
REMINDER_QUOTES = [l.strip()
                   for l in resource_stream(__name__, 'data/reminder_quotes.txt')]


def munge_for_forwarding(message):
    def _(k):
        if k in message: del message[k]

    map(_, ('Delivered-To', 'X-Original-To'))
    message['to'] = BLOG_ADDR

@route('punchit@(host)')
def START(message, host):
    quotes = WELCOME_QUOTES
    confirm.send(relay, 'punchit', message, 'start_confirm.msg', locals())

    return CONFIRMING


@route('punchit-confirm-(id_number)@(host)', id_number='[a-z0-9]+')
def CONFIRMING(message, id_number, host):
    original = confirm.verify('punchit', message['from'], id_number)

    if original:
        munge_for_forwarding(original)

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


@route("(date)-(id_number)@(host)", date='\d{4}\.\d{2}\.\d{2}', id_number='[a-z0-9]+')
def LOG(message, date, id_number, host):
    check = hmac.new(SECRET, message['from']).hexdigest()

    if id_number == check:
        d = datetime.datetime.strptime(date, '%Y.%m.%d')
        message['date'] = d.strftime('%a, %d %b %Y %H:%M:%S +0000')

        munge_for_forwarding(message)

        relay.deliver(message)

        logging.info("%s's Log, supplemental. Stardate: %s", message['from'], d)
    else:
        logging.warning("Transphasic shields holding under assault from %s", message['from'])

    return LOG


@scheduler.interval_schedule(
    days=1,
    start_date=datetime.datetime.now() + datetime.timedelta(minutes=1))
def engage():
    today = datetime.date.today()

    for addr in storage.state_storage.active_addresses():
        def _(d):
            d_str = d.strftime('%Y.%m.%d')
            id_number = hmac.new(SECRET, addr).hexdigest()
            host = FROM_HOST
            quotes = REMINDER_QUOTES

            reminder = view.respond(locals(),
                                   'reminder.msg',
                                   From='%(d_str)s-%(id_number)s@%(host)s',
                                   To=addr,
                                   Subject="Captain's Log, stardate %(d_str)%s")
            relay.deliver(reminder)

        d = storage.reminder_storage.get(addr)

        if d:
            logging.info("Crewman %s's back from an away mission %s", addr, d)

            while d < today:
                _(d)

                d += datetime.timedelta(days=1)
        else:
            logging.info("Crewman %s reporting", addr)

            _(today)

        storage.reminder_storage.set(addr, today)

    logging.info("We've made a full sweep of the system")
