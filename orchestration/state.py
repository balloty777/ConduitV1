from typing import TypedDict
from uuid import UUID
class State(TypedDict):
    request:str
    workflow:str|None
    user_id:UUID
    status:str
    execution_id:UUID|None
    output:str|None
    