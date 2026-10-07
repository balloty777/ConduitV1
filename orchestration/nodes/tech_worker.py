from uuid import UUID
from sqlalchemy.orm import Session
from orchestration.state import State
from llm.openai_service import OpenAIService
from services.approval_service import ApprovalService
from llm.schemas import TechTicketDraft,TechTicketFixDraft
from services.tech_service import TechService

def tech_worker_node(state:State,db:Session)->State:
    llm=OpenAIService().llm
    rejection_reason=state.get("rejection_reason")
    target_id=state.get("target_id")
    prompt = f"""
    Analyze the user's technical request and create a technical support ticket.

    User request:
    {state["request"]}

    The ticket must describe the actual technical problem from the user's request.

    Do not replace the user's problem with generic troubleshooting steps.
    Preserve concrete errors, failing code, expected behavior, actual behavior,
    and relevant technical details when they are present.

    Also propose a concrete technical fix for the problem.

    Extract:
    - title
    - category
    - description
    - proposed_fix
    - priority

    The description must explain WHAT IS ACTUALLY BROKEN.

    The proposed_fix must explain HOW IT SHOULD BE FIXED.
    """
    response=llm.with_structured_output(TechTicketDraft).invoke(prompt)
    service = TechService(db)
    if rejection_reason and target_id:
        ticket = service.update_ticket(ticket_id=target_id, execution_id=state["execution_id"], title=response.title, category=response.category, description=response.description, proposed_fix=response.proposed_fix, priority=response.priority)
    else:
        ticket = service.create_ticket(execution_id=state["execution_id"], title=response.title, category=response.category, description=response.description, proposed_fix=response.proposed_fix, priority=response.priority)
    tool_data = {"ticket_id": str(ticket.id), "execution_id": str(ticket.execution_id), "title": ticket.title, "category": ticket.category, "description": ticket.description, "proposed_fix": ticket.proposed_fix, "priority": ticket.priority, "status": ticket.status}
    approval_service=ApprovalService(db)
    ticket_id=UUID(tool_data["ticket_id"])
    approval_request=approval_service.create_pending(subject_type="tech_ticket",subject_id=UUID(tool_data["ticket_id"]),execution_id=state["execution_id"])
    return {**state,"current_node":"tech_worker","status":"running","output":tool_data,"subject_type":"tech_ticket","approval_request_id":approval_request.id,"subject_id":ticket_id,"target_id":ticket_id,"rejection_reason":None,"error":None}
    
def tech_fix_worker_node(state:State,db:Session)->State:
    llm=OpenAIService().llm
    rejection_reason=state.get("rejection_reason")
    existing_fix_id=state.get("subject_id")
    ticket_id=state.get("target_id")
    if not ticket_id:
        raise ValueError("target id is required to create a technical ticket fix")
    service = TechService(db)
    ticket = service.get_ticket(ticket_id)
    ticket_data = {"ticket_id": str(ticket.id), "title": ticket.title, "category": ticket.category, "description": ticket.description, "proposed_fix": ticket.proposed_fix}
    previous_fix = None
    if rejection_reason and existing_fix_id:
        previous_fix = service.get_ticket_fix(existing_fix_id).proposed_fix
    prompt = f"""
    Generate the corrected code for an existing technical support ticket.

    User request:
    {state["request"]}

    Existing ticket:
    Ticket ID: {ticket_data["ticket_id"]}
    Title: {ticket_data["title"]}
    Category: {ticket_data["category"]}
    Description:
    {ticket_data["description"]}

    Previously proposed fix:
    {ticket_data["proposed_fix"]}
    """

    if rejection_reason:
        prompt += f"""

    The previous generated code fix was rejected:
    {previous_fix}

    Rejection feedback:
    {rejection_reason}

    Revise the fix according to this feedback.
    """

    prompt += """
    Return only the corrected code in the `fixed_code` field.

    Do not return:
    - explanations
    - analysis
    - markdown code fences
    - labels
    - descriptions
    - any text outside the corrected code
    """

    response=llm.with_structured_output(TechTicketFixDraft).invoke(prompt)
    fixed_code=response.fixed_code
    if rejection_reason and existing_fix_id:
        fix = service.update_ticket_fix(fix_id=existing_fix_id, execution_id=state["execution_id"], proposed_fix=fixed_code)
    else:
        fix = service.create_ticket_fix(ticket_id=ticket_id, execution_id=state["execution_id"], proposed_fix=fixed_code)
    tool_data = {"fix_id": str(fix.id), "ticket_id": str(fix.ticket_id), "execution_id": str(fix.execution_id), "proposed_fix": fix.proposed_fix, "status": fix.status}
    approval_service=ApprovalService(db)
    fix_id=UUID(tool_data["fix_id"])
    approval_request=approval_service.create_pending(subject_id=fix_id,subject_type="tech_ticket_fix",execution_id=state["execution_id"])
    return{**state,"current_node":"tech_fix_worker","status":"running","output":tool_data,"subject_type":"tech_ticket_fix","approval_request_id":approval_request.id,"subject_id":fix_id,"target_id":ticket_id,"rejection_reason":None,"error":None}
