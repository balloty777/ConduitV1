from pydantic import BaseModel,Field
from typing import Literal
from datetime import datetime
from uuid import UUID
class JevDepartmentDecision(BaseModel):
    choice:str
    probabilities: dict[str, float]
    confidence:float
    
class MarketingDraft(BaseModel):
    content:str
    platform:Literal["linkedin"]
    tone:str=Field(max_length=50)
    audience:str=Field(max_length=50)
    call_to_action:str |None=Field(default=None,max_length=150)

class SalesLeadDraft(BaseModel):
    name:str=Field(max_length=200)
    email:str
    phone:str|None=Field(default=None,max_length=30)

class SalesFollowUpDraft(BaseModel):
    lead_id:UUID
    message:str
    channel:str

class TechTicketDraft(BaseModel):
    title:str
    category:str
    description:str
    proposed_fix:str
    priority:str

class TechTicketFixDraft(BaseModel):
    fixed_code:str

class JevDecision(BaseModel):
    choice:str
    confidence:float