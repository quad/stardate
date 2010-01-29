import jinja2
import logging
import logging.config

from lamson import confirm, view
from lamson.routing import Router
from lamson.server import Relay

from config import settings
from sqlite_storage import SqliteConfirmationStorage, SqliteStateStorage


logging.config.fileConfig("config/test_logging.conf")

settings.relay = Relay(host=settings.relay_config['host'], 
                       port=settings.relay_config['port'], debug=0)

settings.receiver = None

settings.confirm = confirm.ConfirmationEngine('run/pending',
                                              SqliteConfirmationStorage(':memory:'))

Router.defaults(**settings.router_defaults)
Router.load(settings.handlers)
Router.RELOAD = True
Router.STATE_STORE = SqliteStateStorage(':memory:')
Router.LOG_EXCEPTIONS = False

view.LOADER = jinja2.Environment(
    loader=jinja2.PackageLoader(settings.template_config['dir'], 
                                settings.template_config['module']))
