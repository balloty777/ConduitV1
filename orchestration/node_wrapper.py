from typing import Callable
from sqlalchemy.orm import Session
from orchestration.state import State
from services.workflow_execution_service import WorkflowExecutionService
from exceptions.exceptions import InvalidStateTransitionException
from fastapi.encoders import jsonable_encoder
from langgraph.errors import GraphInterrupt

def run_node(node_name: str,node_fn: Callable[..., State],state: State,db: Session) -> State:
    service = WorkflowExecutionService(db)
    parent_step_id = state.get("current_step_id")

    if state.get("execution_id") is None:
        raise InvalidStateTransitionException("execution_id is required before running a node")

    step = service.create_step(execution_id=state["execution_id"],node=node_name,input_data=jsonable_encoder(dict(state)),parent_step_id=parent_step_id)
    try:
        new_state=node_fn(state,db)
        service.complete_step(step=step,output_data=jsonable_encoder(dict(new_state)))
        new_state["current_step_id"] = step.id
        return new_state
    except GraphInterrupt:
        raise
    except Exception as exc:
        error = str(exc)
        db.rollback()
        service.fail_step(step=step,error=error)
        service.fail_execution(execution_id=state["execution_id"],error=error)
        failed_state = dict(state)
        failed_state["error"] = error
        failed_state["status"] = "failed"
        failed_state["current_step_id"] = step.id

        return failed_state