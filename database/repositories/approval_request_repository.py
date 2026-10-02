from uuid import UUID
from sqlalchemy.orm import Session
from database.models.approval_request import ApprovalRequest

class ApprovalRequestRepository:
    def __init__(self,db:Session):
        self.db=db
    def create(self,approval_request:ApprovalRequest)->ApprovalRequest:
        self.db.add(approval_request)
        self.db.flush()
        return approval_request
    def get_by_id(self,approval_request_id:UUID)->ApprovalRequest:
        return self.db.get(ApprovalRequest,approval_request_id)
    def update(self,approval_request:ApprovalRequest)->ApprovalRequest:
        self.db.flush()
        return approval_request
    def get_by_subject_id(self,subject_id:UUID)->ApprovalRequest|None:
        return(self.db.query(ApprovalRequest).filter(ApprovalRequest.subject_id==subject_id).filter(ApprovalRequest.status=="pending").first())
