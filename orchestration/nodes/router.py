from orchestration.state import State
from llm.jev_service import JevService
from sqlalchemy.orm import Session

DEPARTMENT_QUESTIONS={
    "department":{
        "type":"choice",
        "instructions":"Which Conduit department should handle this request?",
        "criteria": {
            "marketing": "Requests involving marketing campaigns, content creation, promotional content, branding, or audience engagement.",
            "sales": "Requests involving leads, lead creation, prospects, follow-ups, customer outreach, or other sales activities.",
            "tech": "Requests involving technical issues, support tickets, bugs, debugging, fixes, software development, or coding."
        }
    }
}

def router_node(state:State,db:Session)->State:
    jev=JevService()
    decision=jev.decide(state={"request":state["request"]},questions=DEPARTMENT_QUESTIONS)
    return {
        **state,
        "workflow":decision.choice,
        "confidence":decision.confidence,
        "current_node":"router",
        "status":"running"
    }