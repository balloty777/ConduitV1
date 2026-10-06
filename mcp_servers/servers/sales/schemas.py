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
class DeleteLeadInput(BaseModel):
    lead_id: UUID
class DeleteLeadOutput(BaseModel):
    lead_id: UUID
    deleted: bool

class UpdateLeadInput(BaseModel):
    lead_id:UUID
    name:str
    email:str
    phone:str|None=None

class UpdateLeadOutput(BaseModel):
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

class ScheduleFollowUpInput(BaseModel):
    scheduled_at:datetime

class ScheduleFollowUpOutput(BaseModel):
    follow_up_id: UUID
    lead_id: UUID
    execution_id: UUID
    message: str
    channel: str
    status: str
    scheduled_at: datetime
class DeleteFollowUpInput(BaseModel):
    follow_up_id: UUID
class DeleteFollowUpOutput(BaseModel):
    follow_up_id: UUID
    deleted: bool