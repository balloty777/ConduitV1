from uuid import UUID

from database.database import get_session
from orchestration.graph import build_graph
from services.workflow_execution_service import WorkflowExecutionService




state = {
    "request": "Create a marketing campaign for our new product",
    "user_id": UUID("5247c452-360f-4e4d-af2c-dce26bd59b48"),
    "execution_id": None,
    "current_step_id": None,
    "workflow": None,
    "confidence": None,
    "status": "pending",
    "current_node": None,
    "subject_type": None,
    "subject_id": None,
    "approval_request_id": None,
    "rejection_reason": None,
    "output": None,
    "error": None,
}

with get_session() as db:
    execution_service=WorkflowExecutionService(db=db)
    execution=execution_service.create_execution(user_id=state["user_id"],request=state["request"])
    state["execution_id"]=execution.id
    with build_graph(db) as graph:

        result = graph.invoke(state,config={"configurable": {"thread_id": str(state["execution_id"])}})

    print("Final state:")
    print(result)
    print("\nExecution ID:")
    print(state["execution_id"])