from aiogram.filters.callback_data import CallbackData

CHANNELS = 'channels'
ADD_CHANNELS = 'add_channel'
MAIN = 'main'
UNLINK_CHANNEL = 'unlink_channel'
PUBLISH_POST = 'publish_post'
CLEAR_POST = 'clear_post'
CANCEL = 'cancel'
LOOK_SCHEDULE = 'look_schedule'
DELETE_POST = 'delete_post'
NEXT_POST = 'next_post'
PREVIOUS_POST = 'previous_post'
SAVE_POST = 'save_post'
SCHEDULE = 'schedule'

class Channel(CallbackData, prefix='channel'):
    chat_id: int

class WritePost(CallbackData, prefix='channel_write_post'):
    chat_id: int
    edit_mode: bool
    schedule_id: int | None
