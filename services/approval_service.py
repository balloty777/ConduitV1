from uuid import UUID
from sqlalchemy.orm import Session
from database.models.approval_request import ApprovalRequest
from database.repositories.approval_request_repository import ApprovalRequestRepository
from exceptions.exceptions import ResourceNotFoundException,InvalidStateTransitionException
from datetime import datetime
from zoneinfo import ZoneInfo
IST=ZoneInfo("Asia/Kolkata")

class ApprovalService:
    def __init__(self,db:Session):
        self.db=db
        self.approval_repository=ApprovalRequestRepository(db)
    def create_pending(self,subject_type:str,subject_id:UUID,execution_id:UUID,reason:str|None=None)->ApprovalRequest:
        approval_request=ApprovalRequest(subject_type=subject_type,subject_id=subject_id,execution_id=execution_id,status="pending",reason=reason)
        try:
            result=self.approval_repository.create(approval_request)
            self.db.commit()
            self.db.refresh(result)
            return result
        except Exception:
            self.db.rollback()
            raise
    def approve(self,approval_request_id:UUID,decided_by:UUID)->ApprovalRequest:
        approval_request=self.approval_repository.get_by_id(approval_request_id)
        if approval_request is None:
            raise ResourceNotFoundException("Approval request not found")
        if approval_request.status !="pending":
            raise InvalidStateTransitionException(f"Can not approve request with status {approval_request.status}")
        approval_request.status="approved"
        approval_request.decided_by=decided_by
        approval_request.decided_at=datetime.now(IST)
        try:
            result=self.approval_repository.update(approval_request)
            self.db.commit()
            self.db.refresh(result)
            return result
        except Exception:
            self.db.rollback()
            raise
    def reject(self,approval_request_id:UUID,decided_by:UUID,reason:str)->ApprovalRequest:
        approval_request=self.approval_repository.get_by_id(approval_request_id)
        if approval_request is None:
            raise ResourceNotFoundException("Approval request not found")
        if approval_request.status !="pending":
            raise InvalidStateTransitionException(f"Can not reject request with status {approval_request.status}")
        approval_request.status="rejected"
        approval_request.decided_by=decided_by
        approval_request.decided_at=datetime.now(IST)
        try:
            result=self.approval_repository.update(approval_request)
            self.db.commit()
            self.db.refresh(result)
            return result
        except Exception:
            self.db.rollback()
            raise