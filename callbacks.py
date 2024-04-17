from aiogram.filters.callback_data import CallbackData

CHANNELS = 'channels'
ADD_CHANNELS = 'add_channel'
MAIN = 'main'
UNLINK_CHANNEL = 'unlink_channel'
WRITE_POST = 'write_post'
PUBLISH_POST = 'publish_post'
CLEAR_POST = 'clear_post'
CANCEL = 'cancel'
PREVIEW_POST = 'preview_post'
LOOK_SCHEDULE = 'look_schedule'
EDIT_POST = 'edit_post'
DELETE_POST = 'delete_post'
NEXT_POST = 'next_post'
PREVIOUS_POST = 'previous_post'
SAVE_POST = 'save_post'

class Channel(CallbackData, prefix='channel'):
    chat_id: int
