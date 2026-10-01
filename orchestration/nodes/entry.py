from sqlalchemy.orm import Session
from orchestration.state import State
from services.workflow_execution_service import WorkflowExecutionService

def entry_node(state:State,db:Session)->State:
    service = WorkflowExecutionService(db)
    execution=service.create_execution(user_id=state["user_id"],request=state["request"])
    return {**state,"current_node":"entry","status":"running"}