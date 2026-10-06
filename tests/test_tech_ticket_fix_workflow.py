from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.dependencies import get_db
from api.routers.approval import router
from database.database import get_session
from database.models.tech_fix import TechFix
from database.models.tech_ticket import TechTicket
from database.models.user import User
from orchestration.graph import build_graph
from services.workflow_execution_service import WorkflowExecutionService


def create_test_app():
    app = FastAPI()
    app.include_router(router)
    return app


def create_user(db, user_id):
    user = User(
        id=user_id,
        email=f"tech-fix-{uuid4()}@conduit.local",
        role="admin",
        team="Tech",
    )
    db.add(user)
    db.flush()
    return user


def create_ticket(db, user_id):
    execution_service = WorkflowExecutionService(db)

    ticket_execution = execution_service.create_execution(
        user_id=user_id,
        request=(
            "Create a technical support ticket for this bug: "
            "the login endpoint returns HTTP 401 even when valid "
            "credentials are supplied."
        ),
    )

    ticket = TechTicket(
        execution_id=ticket_execution.id,
        title="Login returns HTTP 401 for valid credentials",
        category="authentication",
        description=(
            "The login endpoint returns HTTP 401 even when "
            "valid credentials are supplied."
        ),
        proposed_fix=(
            "Validate the supplied credentials correctly before "
            "returning the authentication failure response."
        ),
        priority="high",
        status="Open",
    )

    db.add(ticket)
    db.flush()

    return ticket


def create_fix_execution(db, user_id, ticket_id):
    execution_service = WorkflowExecutionService(db)

    request = (
        f"Fix the existing technical support ticket {ticket_id}. "
        "Generate the corrected code for the issue described "
        "in that ticket."
    )

    execution = execution_service.create_execution(
        user_id=user_id,
        request=request,
    )

    return execution, request


def build_initial_state(request, user_id, execution_id):
    return {
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
        "target_id": None,
        "approval_request_id": None,
        "rejection_reason": None,
        "output": None,
        "error": None,
    }


def test_tech_ticket_fix_approval_flow():
    user_id = uuid4()

    with get_session() as db:
        create_user(db, user_id)

        ticket = create_ticket(
            db=db,
            user_id=user_id,
        )

        execution, request = create_fix_execution(
            db=db,
            user_id=user_id,
            ticket_id=ticket.id,
        )

        initial_state = build_initial_state(
            request=request,
            user_id=user_id,
            execution_id=execution.id,
        )

        with build_graph(db) as graph:
            result = graph.invoke(
                initial_state,
                config={
                    "configurable": {
                        "thread_id": str(execution.id),
                    }
                },
            )

        assert "__interrupt__" in result

        interrupt = result["__interrupt__"][0].value

        assert interrupt["type"] == "approval_required"
        assert interrupt["subject_type"] == "tech_ticket_fix"
        assert interrupt["subject_id"] is not None
        assert interrupt["approval_request_id"] is not None

        fix = db.get(
            TechFix,
            interrupt["subject_id"],
        )

        assert fix is not None
        assert fix.ticket_id == ticket.id
        assert fix.proposed_fix
        assert fix.proposed_fix.strip()


def test_tech_ticket_fix_rejection_regenerates():
    user_id = uuid4()

    with get_session() as db:
        create_user(db, user_id)

        ticket = create_ticket(
            db=db,
            user_id=user_id,
        )

        execution, request = create_fix_execution(
            db=db,
            user_id=user_id,
            ticket_id=ticket.id,
        )

        initial_state = build_initial_state(
            request=request,
            user_id=user_id,
            execution_id=execution.id,
        )

        with build_graph(db) as graph:
            result = graph.invoke(
                initial_state,
                config={
                    "configurable": {
                        "thread_id": str(execution.id),
                    }
                },
            )

        assert "__interrupt__" in result

        first_interrupt = result["__interrupt__"][0].value

        approval_request_id = first_interrupt[
            "approval_request_id"
        ]

        first_fix_id = first_interrupt["subject_id"]

        assert first_interrupt["subject_type"] == "tech_ticket_fix"

        first_fix = db.get(
            TechFix,
            first_fix_id,
        )

        assert first_fix is not None
        assert first_fix.ticket_id == ticket.id

        app = create_test_app()
        app.dependency_overrides[get_db] = lambda: db

        client = TestClient(app)

        response = client.post(
            f"/approvals/{approval_request_id}/reject",
            json={
                "user_id": str(user_id),
                "reason": (
                    "The proposed fix does not correctly handle "
                    "the authentication failure."
                ),
            },
        )

        assert response.status_code == 200

        with get_session() as verify_db:
            regenerated_fix = verify_db.get(
                TechFix,
                first_fix_id,
            )

            assert regenerated_fix is not None
            assert regenerated_fix.id == first_fix_id
            assert regenerated_fix.ticket_id == ticket.id
            assert regenerated_fix.proposed_fix
            assert regenerated_fix.proposed_fix.strip()


def test_existing_tech_ticket_routes_to_fix_and_generates_code_only():
    user_id = uuid4()

    with get_session() as db:
        create_user(db, user_id)

        ticket = create_ticket(
            db=db,
            user_id=user_id,
        )

        original_proposed_fix = ticket.proposed_fix

        execution, request = create_fix_execution(
            db=db,
            user_id=user_id,
            ticket_id=ticket.id,
        )

        initial_state = build_initial_state(
            request=request,
            user_id=user_id,
            execution_id=execution.id,
        )

        with build_graph(db) as graph:
            result = graph.invoke(
                initial_state,
                config={
                    "configurable": {
                        "thread_id": str(execution.id),
                    }
                },
            )

        assert "__interrupt__" in result

        interrupt = result["__interrupt__"][0].value

        assert interrupt["type"] == "approval_required"
        assert interrupt["subject_type"] == "tech_ticket_fix"
        assert interrupt["subject_id"] is not None
        assert interrupt["approval_request_id"] is not None

        fix = db.get(
            TechFix,
            interrupt["subject_id"],
        )

        assert fix is not None
        assert fix.ticket_id == ticket.id

        proposed_fix = fix.proposed_fix.strip()

        assert proposed_fix
        assert "```" not in proposed_fix

        forbidden_prefixes = (
            "Here is",
            "Here's",
            "The corrected code",
            "Corrected code:",
            "Here is the corrected code",
        )

        assert not proposed_fix.startswith(
            forbidden_prefixes
        )

        assert proposed_fix != original_proposed_fix