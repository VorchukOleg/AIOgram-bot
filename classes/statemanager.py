from .state import State
from utils import Context, get_user_id

states: dict[str, State] = {}

def StateFilter(status: str):
    def check(x: Context):
        return get_user_id(x) in states and states[get_user_id(x)].status == status
    return check

def delete_state(c: Context):
    if get_user_id(c) in states:
        del states[get_user_id(c)]