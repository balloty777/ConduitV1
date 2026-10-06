from langgraph.types import interrupt
from orchestration.state import State
from sqlalchemy.orm import Session

def approval_wait_node(state:State,db:Session)->State:
    if state.get("subject_type") == "tech_ticket":
        message = "Ticket is ready for approval. Approval will generate a code fix for review."
    elif state.get("subject_type") == "tech_ticket_fix":
        message = "Code fix is ready for approval or correction."
    else:
        message = "Content is ready for approval and scheduling"
    decision=interrupt({
        "type":"approval_required",
        "approval_request_id":state["approval_request_id"],
        "subject_type":state["subject_type"],
        "subject_id":state["subject_id"],
        "message":message
    })
    if decision["decision"]=="rejected":
        return{**state,"current_node":"approval_wait","rejection_reason":decision["reason"],"status":"running","error":None}
    return {**state,"current_node":"approval_wait","rejection_reason": None,"status":"completed","error":None}
