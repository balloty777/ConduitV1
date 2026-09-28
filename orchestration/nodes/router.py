from orchestration.state import State
from llm.jev_service import JevService

DEPARTMENT_QUESTIONS={
    "department":{
        "type":"choice",
        "instructions":"Which Conduit department should handle this request?",
        "criteria":{
            "marketing":"Marketing campaigns, content creation, audience entertainment , and promotional command",
            "sales": "Leads,Lead creation, prospect lead, follow-ups with leads, and sales related activity.",
            "tech": "All technical issue resolving,Technical tickets, bugs, fixes, and coding parts.",
        }
    }
}

def router_node(state:State)->State:
    jev=JevService()
    decision=jev.decide(state={"request":state["request"]},questions=DEPARTMENT_QUESTIONS)
    return {
        **state,
        "workflow":decision.choice,
        "confidence":decision.confidence,
        "current_node":"router",
        "status":"running"
    }