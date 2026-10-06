from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.dependencies import get_db
from api.routers.approval import router
from services.approval_service import ApprovalService


def create_test_app():
    app = FastAPI()
    app.include_router(router)
    return app


def test_approve_endpoint_calls_approval_service(monkeypatch):
    approval_id = uuid4()
    execution_id = uuid4()
    subject_id = uuid4()
    user_id = uuid4()

    approval = type(
        "Approval",
        (),
        {
            "id": approval_id,
            "execution_id": execution_id,
            "subject_type": "sales_lead",
            "subject_id": subject_id,
            "status": "approved",
            "reason": None,
            "decided_by": user_id,
        },
    )()

    def fake_approve(
        self,
        approval_request_id,
        decided_by,
        commit,
    ):
        assert approval_request_id == approval_id
        assert decided_by == user_id
        assert commit is True
        return approval

    monkeypatch.setattr(
        ApprovalService,
        "approve",
        fake_approve,
    )

    app = create_test_app()

    app.dependency_overrides[get_db] = lambda: object()

    client = TestClient(app)

    response = client.post(
        f"/approvals/{approval_id}/approve",
        json={
            "user_id": str(user_id),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["approval_request_id"] == str(approval_id)
    assert body["execution_id"] == str(execution_id)
    assert body["subject_type"] == "sales_lead"
    assert body["subject_id"] == str(subject_id)
    assert body["status"] == "approved"
    assert body["decided_by"] == str(user_id)


def test_reject_endpoint_calls_approval_service(monkeypatch):
    approval_id = uuid4()
    execution_id = uuid4()
    subject_id = uuid4()
    user_id = uuid4()

    approval = type(
        "Approval",
        (),
        {
            "id": approval_id,
            "execution_id": execution_id,
            "subject_type": "tech_ticket",
            "subject_id": subject_id,
            "status": "rejected",
            "reason": "Please provide a safer fix.",
            "decided_by": user_id,
        },
    )()

    def fake_reject(
        self,
        approval_request_id,
        decided_by,
        reason,
    ):
        assert approval_request_id == approval_id
        assert decided_by == user_id
        assert reason == "Please provide a safer fix."
        return approval

    monkeypatch.setattr(
        ApprovalService,
        "reject",
        fake_reject,
    )

    app = create_test_app()

    app.dependency_overrides[get_db] = lambda: object()

    client = TestClient(app)

    response = client.post(
        f"/approvals/{approval_id}/reject",
        json={
            "user_id": str(user_id),
            "reason": "Please provide a safer fix.",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["approval_request_id"] == str(approval_id)
    assert body["execution_id"] == str(execution_id)
    assert body["subject_type"] == "tech_ticket"
    assert body["subject_id"] == str(subject_id)
    assert body["status"] == "rejected"
    assert body["reason"] == "Please provide a safer fix."
    assert body["decided_by"] == str(user_id)