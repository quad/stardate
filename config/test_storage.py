from config.settings import confirmation_config, reminder_config, state_config

from stardate.storage import ConfirmationStorage, ReminderDatesStorage, StateStorage

confirm_storage = ConfirmationStorage(':memory:')
reminder_storage = ReminderDatesStorage(':memory:')
state_storage = StateStorage(':memory:')
