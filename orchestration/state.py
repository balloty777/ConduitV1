from typing import TypedDict
from uuid import UUID
class State(TypedDict):
    request:str
    user_id:UUID
    execution_id:UUID|None
    workflow:str|None
    status:str
    current_node:str|None
    subject_type:str|None
    subject_id:str|None
    approval_rquest_id:UUID|None
    approval_reason:str|None
    output:str|None
    error:str|None
    