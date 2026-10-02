from unittest.mock import Mock
from uuid import uuid4
from database.models.approval_request import ApprovalRequest
from database.repositories.approval_request_repository import ApprovalRequestRepository

def test_get_by_subject_id_queries_pending_approval():
    db = Mock()
    repository = ApprovalRequestRepository(db)
    subject_id = uuid4()
    approval = Mock()
    query = Mock()
    filtered_subject = Mock()
    filtered_status = Mock()
    db.query.return_value = query
    query.filter.return_value = filtered_subject
    filtered_subject.filter.return_value = filtered_status
    filtered_status.first.return_value = approval
    result = repository.get_by_subject_id(subject_id)
    assert result is approval
    db.query.assert_called_once_with(ApprovalRequest)
    assert query.filter.call_count == 1
    assert filtered_subject.filter.call_count == 1
    filtered_status.first.assert_called_once()