from uuid import uuid4
from unittest.mock import patch

from orchestration.nodes.approval_wait import approval_wait_node


def make_state():
    return {
        "request": "Create a LinkedIn post for our new product",
        "user_id": uuid4(),
        "execution_id": uuid4(),
        "current_step_id": None,
        "workflow": "marketing",
        "confidence": 1.0,
        "status": "running",
        "current_node": "marketing_worker",
        "subject_type": "marketing_content",
        "subject_id": uuid4(),
        "approval_request_id": uuid4(),
        "rejection_reason": None,
        "output": None,
        "error": None,
    }


def test_approval_wait_rejected_stores_reason():
    state = make_state()

    with patch(
        "orchestration.nodes.approval_wait.interrupt",
        return_value={
            "decision": "rejected",
            "reason": "Please make the CTA more specific",
        },
    ) as mock_interrupt:
        result = approval_wait_node(state, None)

    mock_interrupt.assert_called_once_with(
        {
            "type": "approval_required",
            "approval_request_id": state["approval_request_id"],
            "subject_type": state["subject_type"],
            "subject_id": state["subject_id"],
            "message": "Content is ready for approval and scheduling",
        }
    )

    assert result["current_node"] == "approval_wait"
    assert result["rejection_reason"] == "Please make the CTA more specific"


def test_approval_wait_approved_clears_rejection_reason():
    state = make_state()
    state["rejection_reason"] = "Old rejection feedback"

    with patch(
        "orchestration.nodes.approval_wait.interrupt",
        return_value={
            "decision": "approved",
        },
    ) as mock_interrupt:
        result = approval_wait_node(state, None)

    mock_interrupt.assert_called_once_with(
        {
            "type": "approval_required",
            "approval_request_id": state["approval_request_id"],
            "subject_type": state["subject_type"],
            "subject_id": state["subject_id"],
            "message": "Content is ready for approval and scheduling",
        }
    )

    assert result["current_node"] == "approval_wait"
    assert result["rejection_reason"] is None