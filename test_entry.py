from uuid import UUID

from database.database import get_session
from orchestration.nodes.entry import entry_node
from orchestration.state import State


user_id = UUID("2bf55f52-38fa-45ac-a17e-155317169a54")

state: State = {
    "request": "Create a Diwali marketing campaign.",
    "user_id": user_id,
    "execution_id": None,
    "current_step_id": None,
    "workflow": None,
    "confidence": None,
    "status": "pending",
    "current_node": None,
    "subject_type": None,
    "subject_id": None,
    "approval_request_id": None,
    "approval_reason": None,
    "output": None,
    "error": None,
}

with get_session() as db:
    result = entry_node(state, db)

    print("Execution ID:", result["execution_id"])
    print("Current node:", result["current_node"])
    print("Status:", result["status"])