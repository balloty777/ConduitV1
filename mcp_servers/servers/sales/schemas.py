from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class CreateLeadInput(BaseModel):
    execution_id:UUID
    name:str
    email:str
    phone:str|None=None
class CreateLeadOutput(BaseModel):
    lead_id:UUID
    execution_id:UUID
    name:str
    email:str
    phone:str|None=None
    status:str
class FollowUpLeadInput(BaseModel):
    lead_id:UUID
    execution_id:UUID
    message:str
    channel:str
    scheduled_at:datetime|None=None
class FollowUpLeadOutput(BaseModel):
    follow_up_id:UUID
    lead_id:UUID
    execution_id:UUID
    message:str
    channel:str
    status:str
    scheduled_at: datetime | None=None