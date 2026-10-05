from orchestration.state import State
from llm.jev_service import JevService
from sqlalchemy.orm import Session

ROUTING_QUESTIONS = {
    "route": {
        "type": "choice",
        "instructions": "Which Conduit workflow and action should handle this request?",
        "criteria": {
            "marketing_create_content": (
                "Marketing requests involving campaigns, content creation, "
                "promotional content, branding, or audience engagement."
            ),
            "sales_create_lead": (
                "Sales requests asking to create, add, capture, or register "
                "a new lead or prospect."
            ),
            "sales_follow_up": (
                "Sales requests asking to follow up with, contact, message, "
                "or reach out to an existing lead or prospect."
            ),
            "tech_create_ticket": (
                "Technical requests involving a new issue, bug, support "
                "request, incident, or problem that should become a ticket."
            ),
            "tech_create_ticket_fix": (
                "Technical requests asking to propose, create, or apply a "
                "fix or solution for an existing technical ticket or issue."
            ),
        },
    }
}
ROUTE_MAPPING = {
    "marketing_create_content": ("marketing", "create_content"),
    "sales_create_lead": ("sales", "create_lead"),
    "sales_follow_up": ("sales", "follow_up_lead"),
    "tech_create_ticket": ("tech", "create_ticket"),
    "tech_create_ticket_fix": ("tech", "create_ticket_fix")
}

def router_node(state:State,db:Session)->State:
    jev=JevService()
    decision=jev.decide(state={"request":state["request"]},questions=ROUTING_QUESTIONS)
    workflow,action=ROUTE_MAPPING[decision.choice]
    return {
        **state,
        "workflow":workflow,
        "action":action,
        "confidence":decision.confidence,
        "current_node":"router",
        "status":"running"
    }