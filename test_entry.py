from uuid import UUID

from database.database import get_session
from orchestration.nodes.entry import entry_node
from orchestration.state import State


user_id = UUID("2bf55f52-38fa-45ac-a17e-155317169a54")
execution_id=UUID("9a9edfb6-40fc-4c2f-99e9-11ebd5b12266")
subject_id=UUID("b5ae0402-4ff7-4de7-bc10-11f71cb7c152")
arid=UUID("090711e4-88fd-431e-952a-ad52a098c2bc")
state: State = {
    "request": "Create a Diwali marketing campaign.",
    "user_id": user_id,
    "execution_id": execution_id,
    "current_step_id": None,
    "workflow": None,
    "confidence": None,
    "status": "pending",
    "current_node": None,
    "subject_type": None,
    "subject_id": subject_id,
    "approval_request_id": arid,
    "approval_reason": None,
    "output": None,
    "error": None,
}

with get_session() as db:
    result = entry_node(state, db)

    print("Execution ID:", result["execution_id"])
    print("Current node:", result["current_node"])
    print("Status:", result["status"])