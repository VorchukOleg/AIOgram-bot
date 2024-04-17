from .post import Post

class State:
    status: str 
    chat_id: int | None = None
    post: Post | None = None

    # Looking schedule
    page: int | None = None

    # Editing
    schedule_id: int | None

    def __init__(self, status: str = '', chat_id: int | None = None, post: Post | None = None,
                 page: int | None = None, schedule_id: int | None= None):
        self.status = status
        self.chat_id = chat_id
        self.post = post
        self.page = page
        self.schedule_id = schedule_id

    def __str__(self) -> str:
        return f'({self.status}, {self.chat_id or 'None'}, {self.post or 'None'})'