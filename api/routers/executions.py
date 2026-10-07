from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.dependencies import get_db
from database.database import get_session
from database.models.execution_steps import ExecutionStep
from database.models.user import User
from database.models.workflow_execution import WorkflowExecution
from orchestration.graph import build_graph
from services.workflow_execution_service import WorkflowExecutionService

router = APIRouter(tags=["Executions"])


def _execution_action(execution: WorkflowExecution) -> str | None:
    for step in reversed(sorted(execution.steps, key=lambda item: item.created_at)):
        output = step.output_data or {}
        if output.get("action"):
            return output["action"]
    return None


def _step_data(step: ExecutionStep) -> dict:
    return {
        "step_id": str(step.id),
        "node": step.node,
        "status": step.status,
        "created_at": step.created_at,
        "updated_at": step.updated_at,
        "input_data": step.input_data,
        "output_data": step.output_data,
    }


def _execution_data(execution: WorkflowExecution, include_steps: bool = False) -> dict:
    data = {
        "execution_id": str(execution.id),
        "user_id": str(execution.user_id),
        "request": execution.request,
        "workflow": execution.workflow,
        "action": _execution_action(execution),
        "status": execution.status,
        "result": execution.result,
        "created_at": execution.created_at,
        "updated_at": execution.updated_at,
    }
    if include_steps:
        data["steps"] = [_step_data(step) for step in sorted(execution.steps, key=lambda item: item.created_at)]
    return data


def _run_execution(execution_id: UUID) -> None:
    with get_session() as db:
        execution = db.get(WorkflowExecution, execution_id)
        if execution is None:
            return
        initial_state = {
            "request": execution.request,
            "user_id": execution.user_id,
            "execution_id": execution.id,
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
        try:
            with build_graph(db) as graph:
                result = graph.invoke(
                    initial_state,
                    config={"configurable": {"thread_id": str(execution.id)}},
                )
            execution.workflow = result.get("workflow")
            if "__interrupt__" in result and execution.status == "running":
                execution.status = "waiting"
                db.commit()
        except Exception as exc:
            db.rollback()
            current = db.get(WorkflowExecution, execution_id)
            if current is not None and current.status == "running":
                WorkflowExecutionService(db).fail_execution(execution_id, str(exc))


@router.post("/executions", status_code=status.HTTP_202_ACCEPTED)
def launch_execution(data: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    request_text = str(data.get("request", "")).strip()
    if not request_text:
        raise HTTPException(status_code=422, detail="request is required")

    user_id_value = data.get("user_id")
    if user_id_value:
        try:
            user_id = UUID(str(user_id_value))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="user_id must be a UUID") from exc
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
    else:
        user = db.query(User).first()
        if user is None:
            user = User(email="operator@conduit.local", role="admin", team="Operations")
            db.add(user)
            db.commit()
            db.refresh(user)
        user_id = user.id

    execution = WorkflowExecutionService(db).create_execution(user_id=user_id, request=request_text)
    background_tasks.add_task(_run_execution, execution.id)
    return {"execution_id": str(execution.id), "status": execution.status}


@router.get("/executions")
def list_executions(limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)):
    executions = (
        db.query(WorkflowExecution)
        .order_by(WorkflowExecution.updated_at.desc())
        .limit(limit)
        .all()
    )
    return [_execution_data(execution) for execution in executions]


@router.get("/executions/{execution_id}")
def get_execution(execution_id: UUID, db: Session = Depends(get_db)):
    execution = db.get(WorkflowExecution, execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")
    return _execution_data(execution, include_steps=True)


@router.get("/approvals")
def list_approvals(status_filter: str | None = Query(default=None, alias="status"), db: Session = Depends(get_db)):
    from database.models.approval_request import ApprovalRequest

    query = db.query(ApprovalRequest)
    if status_filter:
        query = query.filter(ApprovalRequest.status == status_filter)
    rows = query.order_by(ApprovalRequest.created_at.desc()).limit(500).all()
    return [
        {
            "approval_request_id": str(row.id),
            "subject_type": row.subject_type,
            "subject_id": str(row.subject_id),
            "execution_id": str(row.execution_id),
            "status": row.status,
            "reason": row.reason,
            "decided_by": str(row.decided_by) if row.decided_by else None,
            "created_at": row.created_at,
            "decided_at": row.decided_at,
        }
        for row in rows
    ]
