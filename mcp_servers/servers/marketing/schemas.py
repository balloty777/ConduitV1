from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
class DraftContentInput(BaseModel):
    execution_id:UUID
    brief:str
    platform:str
    tone:str
    audience:str
    call_to_action:str|None=None
class DraftContentOutput(BaseModel):
    content_id:UUID
    platform:str
    content:str
    status:str
class GetContentInput(BaseModel):
    content_id:UUID
class GetContentOutput(BaseModel):
    content_id:UUID
    platform:str
    content:str
    status:str
class ScheduleContentInput(BaseModel):
    scheduled_at:datetime
class ScheduleContentOutput(BaseModel):
    content_id:UUID
    platform:str
    status:str
    scheduled_at:datetime|None=None
    