from config.settings import confirmation_config, state_config

from stardate.storage import ConfirmationStorage, StateStorage

confirm_storage = ConfirmationStorage(':memory:')
state_storage = StateStorage(':memory:')
