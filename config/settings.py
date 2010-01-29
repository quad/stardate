BLOG_ADDR = 'post@posterous.com'

# You may add additional parameters such as `username' and `password' if your
# relay server requires authentication, `starttls' (boolean) or `ssl' (boolean)
# for secure connections.
relay_config = {'host': 'localhost', 'port': 8825}
receiver_config = {'host': 'localhost', 'port': 8823}

handlers = ['stardate.handlers']
router_defaults = {'host': '.+'}
template_config = {'dir': 'stardate', 'module': 'templates'}

# confirm subscriptions
from lamson import confirm

confirm = confirm.ConfirmationEngine('run/pending',
                                     confirm.ConfirmationStorage())
