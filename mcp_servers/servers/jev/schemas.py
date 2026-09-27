from pydantic import BaseModel

class JevDepartmentDecision(BaseModel):
    choice:str
    probabilities: dict[str, float]
    confidence:float
    