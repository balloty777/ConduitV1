from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from main import app
from database.database import get_session
from database.models.approval_request import ApprovalRequest
from database.models.sales_follow_ups import SalesFollowUp
from database.models.sales_lead import SalesLead
from database.models.user import User
from database.models.workflow_execution import WorkflowExecution
from orchestration.graph import build_graph
from services.workflow_execution_service import WorkflowExecutionService


client = TestClient(app)


def test_sales_follow_up_rejection_regenerates():
    user_id = uuid4()
    lead_id = uuid4()

    request = (
        "Follow up with the existing sales lead "
        "and schedule the follow-up after approval"
    )

    with get_session() as db:
        user = User(
            id=user_id,
            email=f"sales-rejection-test-{uuid4()}@conduit.local",
            role="admin",
            team="Sales",
        )

        db.add(user)
        db.flush()

        execution_service = WorkflowExecutionService(db)

        execution = execution_service.create_execution(
            user_id=user_id,
            request=request,
        )

        execution_id = execution.id

        lead = SalesLead(
            id=lead_id,
            execution_id=execution_id,
            name="Test Lead",
            email=f"lead-{uuid4()}@example.com",
            phone="9999999999",
        )

        db.add(lead)
        db.commit()

        initial_state = {
            "request": request,
            "user_id": user_id,
            "execution_id": execution_id,
            "current_step_id": None,
            "workflow": None,
            "action": None,
            "confidence": None,
            "status": "running",
            "current_node": None,
            "subject_type": None,
            "subject_id": None,
            "target_id": lead_id,
            "approval_request_id": None,
            "rejection_reason": None,
            "output": None,
            "error": None,
        }

        first_draft = Mock()
        first_draft.lead_id = lead_id
        first_draft.message = "Initial follow-up message."
        first_draft.channel = "email"

        second_draft = Mock()
        second_draft.lead_id = lead_id
        second_draft.message = "Revised follow-up message."
        second_draft.channel = "email"

        with patch(
            "orchestration.nodes.router.JevService"
        ) as mock_jev, patch(
            "orchestration.nodes.sales_worker.OpenAIService"
        ) as mock_openai:

            mock_jev.return_value.decide.return_value = Mock(
                choice="sales_follow_up",
                confidence=1.0,
            )

            mock_llm = (
                mock_openai.return_value
                .llm
                .with_structured_output
                .return_value
            )

            mock_llm.invoke.side_effect = [
                first_draft,
                second_draft,
            ]

            with build_graph(db) as graph:
                config = {
                    "configurable": {
                        "thread_id": str(execution_id)
                    }
                }

                result = graph.invoke(
                    initial_state,
                    config=config,
                )

            assert "__interrupt__" in result

            first_interrupt = result["__interrupt__"][0].value

            assert first_interrupt["type"] == "approval_required"
            assert first_interrupt["subject_type"] == "sales_follow_up"

            first_follow_up_id = first_interrupt["subject_id"]

        first_approval = (
            db.query(ApprovalRequest)
            .filter(
                ApprovalRequest.execution_id == execution_id,
                ApprovalRequest.subject_type == "sales_follow_up",
                ApprovalRequest.subject_id == first_follow_up_id,
                ApprovalRequest.status == "pending",
            )
            .order_by(ApprovalRequest.created_at.desc())
            .first()
        )

        assert first_approval is not None

        first_approval_id = first_approval.id

    # Reject the first follow-up.
    response = client.post(
        f"/approvals/{first_approval_id}/reject",
        json={
            "user_id": str(user_id),
            "reason": "Make the message more specific to the customer.",
        },
    )

    assert response.status_code == 200, response.text

    # The graph should have regenerated the follow-up
    # and created another pending approval.
    with get_session() as db:
        first_approval = db.get(
            ApprovalRequest,
            first_approval_id,
        )

        assert first_approval.status == "rejected"
        assert (
            first_approval.reason
            == "Make the message more specific to the customer."
        )

        second_approval = (
            db.query(ApprovalRequest)
            .filter(
                ApprovalRequest.execution_id == execution_id,
                ApprovalRequest.subject_type == "sales_follow_up",
                ApprovalRequest.status == "pending",
            )
            .order_by(ApprovalRequest.created_at.desc())
            .first()
        )

        assert second_approval is not None
        assert second_approval.id != first_approval_id
        assert second_approval.subject_id != first_follow_up_id

        second_follow_up = db.get(
            SalesFollowUp,
            second_approval.subject_id,
        )

        assert second_follow_up is not None
        assert second_follow_up.message is not None
        assert second_follow_up.message != "Initial follow-up message."
        assert second_follow_up.scheduled_at is None

        second_approval_id = second_approval.id
        second_follow_up_id = second_approval.subject_id

    # Approve the regenerated follow-up.
    response = client.post(
        f"/approvals/{second_approval_id}/approve",
        json={
            "user_id": str(user_id),
        },
    )

    assert response.status_code == 200, response.text

    with get_session() as db:
        execution = db.get(
            WorkflowExecution,
            execution_id,
        )

        second_follow_up = db.get(
            SalesFollowUp,
            second_follow_up_id,
        )

        assert second_follow_up is not None
        assert second_follow_up.scheduled_at is None
        assert execution.status != "completed"

    # Schedule the regenerated follow-up.
    scheduled_at = (
        datetime.now().astimezone() + timedelta(hours=1)
    )

    response = client.post(
        f"/sales/leads/follow-up/{second_follow_up_id}/schedule",
        json={
            "scheduled_at": scheduled_at.isoformat(),
        },
    )

    assert response.status_code == 200, response.text

    with get_session() as db:
        second_follow_up = db.get(
            SalesFollowUp,
            second_follow_up_id,
        )

        execution = db.get(
            WorkflowExecution,
            execution_id,
        )

        assert second_follow_up.scheduled_at is not None
        assert execution.status == "completed"