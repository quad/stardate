from config.settings import confirmation_config, state_config

from stardate.storage import ConfirmationStorage, StateStorage

confirm_storage = ConfirmationStorage(confirmation_config['store'])
state_storage = StateStorage(state_config['store'])
