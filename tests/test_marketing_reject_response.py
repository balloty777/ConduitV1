from uuid import uuid4
from unittest.mock import MagicMock, patch

from api.routers.marketing import reject_content


def test_reject_content_returns_new_generated_content_and_approval():
    old_content_id = uuid4()
    old_approval_id = uuid4()

    new_content_id = uuid4()
    new_approval_id = uuid4()

    user_id = uuid4()
    execution_id = uuid4()

    db = MagicMock()

    old_approval = MagicMock()
    old_approval.id = old_approval_id
    old_approval.execution_id = execution_id

    rejected_approval = MagicMock()
    rejected_approval.id = old_approval_id
    rejected_approval.status = "rejected"
    rejected_approval.reason = "Make the CTA stronger"

    resumed_state = {
        "subject_id": new_content_id,
        "approval_request_id": new_approval_id,
    }

    with patch(
        "api.routers.marketing.ApprovalService"
    ) as mock_approval_service, patch(
        "api.routers.marketing.build_graph"
    ) as mock_build_graph:

        approval_service = mock_approval_service.return_value
        approval_service.get_pending_by_subject_id.return_value = old_approval
        approval_service.reject.return_value = rejected_approval

        graph = mock_build_graph.return_value.__enter__.return_value
        graph.invoke.return_value = resumed_state

        result = reject_content(
            content_id=old_content_id,
            data=MagicMock(reason="Make the CTA stronger"),
            user_id=user_id,
            db=db,
        )

    assert result["content_id"] == new_content_id
    assert result["approval_request_id"] == new_approval_id
    assert result["status"] == "pending"
    assert result["reason"] == "Make the CTA stronger"