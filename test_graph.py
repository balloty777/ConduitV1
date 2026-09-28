from uuid import UUID

from database.database import get_session
from orchestration.graph import build_graph





state = {
    "request": "Create a marketing campaign for our new product",
    "user_id": UUID("e2360e81-0086-455f-8c01-ba0a47cca3ec"),
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
    graph = build_graph(db)

    result = graph.invoke(state)

    print("Final state:")
    print(result)