from pydantic import BaseModel,Field
from typing import Literal
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