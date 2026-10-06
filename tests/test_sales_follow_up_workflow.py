import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from main import app
from database.database import get_session
from database.models.workflow_execution import WorkflowExecution
from database.models.sales_follow_ups import SalesFollowUp
from database.models.approval_request import ApprovalRequest


client = TestClient(app)


def get_db():
    with get_session() as db:
        yield db


def test_sales_follow_up_approval_and_scheduling():
    user_id = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())

    # 1. Start the workflow
    response = client.post(
        "/workflow/execute",
        json={
            "request": "Create a follow-up message for the sales lead and schedule it after approval",
            "user_id": user_id,
            "execution_id": execution_id,
        },
    )

    assert response.status_code in (200, 201), response.text

    # 2. Find the pending approval created by the worker
    with get_session() as db:
        approval = (
            db.query(ApprovalRequest)
            .filter(
                ApprovalRequest.execution_id == uuid.UUID(execution_id),
                ApprovalRequest.subject_type == "sales_follow_up",
                ApprovalRequest.status == "pending",
            )
            .order_by(ApprovalRequest.created_at.desc())
            .first()
        )

        assert approval is not None

        approval_id = str(approval.id)
        follow_up_id = str(approval.subject_id)

    # 3. Approve the follow-up
    response = client.post(
        f"/approvals/{approval_id}/approve",
        json={"user_id": user_id},
    )

    assert response.status_code == 200, response.text

    # 4. Verify approval happened but execution is NOT completed yet
    with get_session() as db:
        approval = db.get(
            ApprovalRequest,
            uuid.UUID(approval_id),
        )

        execution = db.get(
            WorkflowExecution,
            uuid.UUID(execution_id),
        )

        follow_up = db.get(
            SalesFollowUp,
            uuid.UUID(follow_up_id),
        )

        assert approval.status == "approved"
        assert follow_up is not None
        assert follow_up.scheduled_at is None

        # Scheduling is now a separate human action.
        assert execution.status != "completed"

    # 5. Manually schedule the approved follow-up
    scheduled_at = (
        datetime.now().astimezone() + timedelta(hours=1)
    )

    response = client.post(
        f"/sales/leads/follow-up/{follow_up_id}/schedule",
        json={
            "scheduled_at": scheduled_at.isoformat(),
        },
    )

    assert response.status_code == 200, response.text

    # 6. Verify final state
    with get_session() as db:
        follow_up = db.get(
            SalesFollowUp,
            uuid.UUID(follow_up_id),
        )

        execution = db.get(
            WorkflowExecution,
            uuid.UUID(execution_id),
        )

        assert follow_up.scheduled_at is not None
        assert execution.status == "completed"