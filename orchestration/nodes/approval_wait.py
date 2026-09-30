from langgraph.types import interrupt
from orchestration.state import State

def approval_wait_node(state:State)->State:
    interrupt({
        "type":"approval_required",
        "approcal_request_id":state["approval_request_id"],
        "subject_type":state["subject_type"],
        "subject_id":state["subject_id"],
        "message":"Content is ready for approval and scheduling"
    })
    return {**state,"current_node":"approval_wait"}