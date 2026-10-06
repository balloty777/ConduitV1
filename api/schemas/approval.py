from pydantic import BaseModel,Field
from uuid import UUID

class ApproveApprovalRequest(BaseModel):
    user_id:UUID

class RejectApprovalRequest(BaseModel):
    user_id:UUID
    reason:str=Field(min_length=1)

class ApprovalResponse(BaseModel):
    approval_request_id:UUID
    execution_id:UUID
    subject_type:str
    subject_id:UUID
    status:str
    reason:str|None=None
    decided_by:UUID|None=None
