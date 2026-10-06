from langgraph.types import interrupt
from orchestration.state import State
from sqlalchemy.orm import Session

def approval_wait_node(state:State,db:Session)->State:
    decision=interrupt({
        "type":"approval_required",
        "approval_request_id":state["approval_request_id"],
        "subject_type":state["subject_type"],
        "subject_id":state["subject_id"],
        "message":"Content is ready for approval and scheduling"
    })
    if decision["decision"]=="rejected":
        return{**state,"current_node":"approval_wait","rejection_reason":decision["reason"],"status":"running","error":None}
    return {**state,"current_node":"approval_wait","error": None,"rejection_reason": None,"status":"completed","error":None}