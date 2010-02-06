import jinja2
import logging
import logging.config

from apscheduler.scheduler import Scheduler

from lamson import confirm, view
from lamson.routing import Router
from lamson.server import Relay

import config.test_storage

from config import settings
from config.test_storage import confirm_storage, state_storage


logging.config.fileConfig("config/test_logging.conf")

settings.relay = Relay(host=settings.relay_config['host'], 
                       port=settings.relay_config['port'], debug=0)

settings.receiver = None

settings.confirm = confirm.ConfirmationEngine(
    settings.confirmation_config['queue'],
    confirm_storage)

settings.storage = config.test_storage

settings.scheduler = Scheduler()

Router.defaults(**settings.router_defaults)
Router.load(settings.handlers)
Router.RELOAD = True
Router.STATE_STORE = state_storage
Router.LOG_EXCEPTIONS = False

view.LOADER = jinja2.Environment(
    loader=jinja2.PackageLoader(settings.template_config['dir'], 
                                settings.template_config['module']))
