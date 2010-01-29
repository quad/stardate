import jinja2
import logging
import logging.config

from lamson import confirm, view, queue
from lamson.routing import Router
from lamson.server import Relay, SMTPReceiver

from config import settings
from config.storage import confirm_storage, state_storage


logging.config.fileConfig('config/logging.conf')

settings.relay = Relay(host=settings.relay_config['host'], 
                       port=settings.relay_config['port'], debug=0)

settings.receiver = SMTPReceiver(settings.receiver_config['host'],
                                 settings.receiver_config['port'])

settings.confirm = confirm.ConfirmationEngine(
    settings.confirmation_config['queue'],
    confirm_storage)

Router.defaults(**settings.router_defaults)
Router.load(settings.handlers)
Router.RELOAD = True
Router.STATE_STORE = state_storage
Router.UNDELIVERABLE_QUEUE = queue.Queue('run/undeliverable')

view.LOADER = jinja2.Environment(
    loader=jinja2.PackageLoader(settings.template_config['dir'],
                                settings.template_config['module']))
