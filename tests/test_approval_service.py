from unittest.mock import Mock
from uuid import uuid4
from services.approval_service import ApprovalService
import pytest
from exceptions.exceptions import ResourceAlreadyExist,ResourceNotFoundException,InvalidStateTransitionException

def make_service():
    db=Mock()
    service=ApprovalService(db)
    service.approval_repository=Mock()
    return service,db

def test_create_pending_creates_pending_approval():
    service,db=make_service()
    subject_id=uuid4()
    execution_id=uuid4()
    create_approval=Mock()
    service.approval_repository.create.return_value=create_approval
    result=service.create_pending(subject_type="marketing_content",subject_id=subject_id,execution_id=execution_id,reason=None)
    created_request=service.approval_repository.create.call_args.args[0]
    assert result is create_approval
    assert created_request.subject_type=="marketing_content"
    assert created_request.subject_id==subject_id
    assert created_request.execution_id==execution_id
    assert created_request.status=="pending"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(create_approval)

def test_approve_pending_request():
    service, db = make_service()
    approval_id = uuid4()
    decided_by = uuid4()
    approval = Mock()
    approval.status = "pending"
    service.approval_repository.get_by_id.return_value = approval
    service.approval_repository.update.return_value = approval
    result = service.approve(approval_request_id=approval_id,decided_by=decided_by)
    assert result is approval
    assert approval.status == "approved"
    assert approval.decided_by == decided_by
    assert approval.decided_at is not None
    service.approval_repository.get_by_id.assert_called_once_with(approval_id)
    service.approval_repository.update.assert_called_once_with(approval)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(approval)


def test_reject_pending_request():
    service, db = make_service()
    approval_id = uuid4()
    decided_by = uuid4()
    reason = "Please make the CTA more specific."
    approval = Mock()
    approval.status = "pending"
    service.approval_repository.get_by_id.return_value = approval
    service.approval_repository.update.return_value = approval
    result = service.reject(approval_request_id=approval_id,decided_by=decided_by,reason=reason)
    assert result is approval
    assert approval.status == "rejected"
    assert approval.decided_by == decided_by
    assert approval.decided_at is not None
    assert approval.reason == reason
    service.approval_repository.get_by_id.assert_called_once_with(approval_id)
    service.approval_repository.update.assert_called_once_with(approval)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(approval)


def test_cannot_approve_non_pending_request():
    service, _ = make_service()
    approval_id = uuid4()
    approval = Mock()
    approval.status = "approved"
    service.approval_repository.get_by_id.return_value = approval
    with pytest.raises(InvalidStateTransitionException):
        service.approve(approval_request_id=approval_id,decided_by=uuid4())
    service.approval_repository.update.assert_not_called()

def test_cannot_reject_non_pending_request():
    service, _ = make_service()
    approval_id = uuid4()
    approval = Mock()
    approval.status = "rejected"
    service.approval_repository.get_by_id.return_value = approval
    with pytest.raises(InvalidStateTransitionException):
        service.reject(approval_request_id=approval_id,decided_by=uuid4(),reason="Another change needed.")
    service.approval_repository.update.assert_not_called()

def test_approve_missing_request():
    service, _ = make_service()
    service.approval_repository.get_by_id.return_value = None
    with pytest.raises(ResourceNotFoundException):
        service.approve(approval_request_id=uuid4(),decided_by=uuid4())

def test_reject_missing_request():
    service, _ = make_service()
    service.approval_repository.get_by_id.return_value = None
    with pytest.raises(ResourceNotFoundException):
        service.reject(approval_request_id=uuid4(),decided_by=uuid4(),reason="Needs revision.")

def test_get_pending_by_subject_id_returns_approval():
    db = Mock()
    service = ApprovalService(db)
    approval = Mock()
    subject_id = uuid4()
    service.approval_repository = Mock()
    service.approval_repository.get_by_subject_id.return_value = approval
    result = service.get_pending_by_subject_id(subject_id)
    assert result is approval
    service.approval_repository.get_by_subject_id.assert_called_once_with(subject_id)

def test_get_pending_by_subject_id_raises_when_missing():
    db = Mock()
    service = ApprovalService(db)
    subject_id = uuid4()
    service.approval_repository = Mock()
    service.approval_repository.get_by_subject_id.return_value = None
    with pytest.raises(ResourceNotFoundException):
        service.get_pending_by_subject_id(subject_id)
    service.approval_repository.get_by_subject_id.assert_called_once_with(subject_id)