from aiogram.filters.callback_data import CallbackData

CHANNELS = 'channels'
ADD_CHANNELS = 'add_channel'
MAIN = 'main'
UNLINK_CHANNEL = 'unlink_channel'
PUBLISH_POST = 'publish_post'
CANCEL = 'cancel'
LOOK_SCHEDULE = 'look_schedule'
DELETE_POST = 'delete_post'
NEXT_POST = 'next_post'
PREVIOUS_POST = 'previous_post'
SAVE_POST = 'save_post'
SCHEDULE = 'schedule'
SET_BUTTONS = 'set_buttons'
CLEAR_MEDIA = 'clear_media'
CLEAR_TEXT = 'clear_text'

class Channel(CallbackData, prefix='channel'):
    chat_id: int

class WritePost(CallbackData, prefix='channel_write_post'):
    chat_id: int
    edit_mode: bool
    schedule_id: int | None

class EditCreatedPost(CallbackData, prefix='edit_post'):
    chat_id: int
