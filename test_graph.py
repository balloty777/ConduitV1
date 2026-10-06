from uuid import UUID

from database.database import get_session
from services.workflow_execution_service import WorkflowExecutionService
from orchestration.graph import build_graph


USER_ID = UUID(
    "e2360e81-0086-455f-8c01-ba0a47cca3ec"
)

TICKET_ID = UUID(
    "068fe98b-0e60-42f6-8b50-4b0b9f211959"
)

REQUEST = (
    "Generate the corrected code for the approved technical ticket."
)


with get_session() as db:
    execution_service = WorkflowExecutionService(db)

    execution = execution_service.create_execution(
        user_id=USER_ID,
        request=REQUEST,
    )

    execution_id = execution.id

    initial_state = {
        "request": REQUEST,
        "user_id": USER_ID,
        "execution_id": execution_id,
        "current_step_id": None,
        "workflow": "tech",
        "action": "create_ticket_fix",
        "confidence": 1.0,
        "status": "running",
        "current_node": None,
        "subject_type": None,
        "subject_id": None,
        "target_id": TICKET_ID,
        "approval_request_id": None,
        "rejection_reason": None,
        "output": None,
        "error": None,
    }

    with build_graph(db) as graph:
        result = graph.invoke(
            initial_state,
            config={
                "configurable": {
                    "thread_id": str(execution_id)
                }
            },
        )

        print("\n=== TECH FIX INITIAL RUN ===")
        print("EXECUTION ID:", execution_id)
        print("STATUS:", result.get("status"))
        print("CURRENT NODE:", result.get("current_node"))
        print("WORKFLOW:", result.get("workflow"))
        print("ACTION:", result.get("action"))
        print("CONFIDENCE:", result.get("confidence"))
        print("SUBJECT TYPE:", result.get("subject_type"))
        print("SUBJECT ID:", result.get("subject_id"))
        print("TARGET ID:", result.get("target_id"))
        print("APPROVAL REQUEST ID:", result.get("approval_request_id"))
        print("OUTPUT:", result.get("output"))
        print("REJECTION REASON:", result.get("rejection_reason"))
        print("ERROR:", result.get("error"))