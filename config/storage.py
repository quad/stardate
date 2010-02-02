from config.settings import confirmation_config, reminder_config, state_config

from stardate.storage import ConfirmationStorage, ReminderDatesStorage, StateStorage

confirm_storage = ConfirmationStorage(confirmation_config['store'])
reminder_storage = ReminderDatesStorage(reminder_config['store'])
state_storage = StateStorage(state_config['store'])
