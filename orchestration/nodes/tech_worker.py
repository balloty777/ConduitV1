from uuid import UUID
import json
from sqlalchemy.orm import Session
from orchestration.state import State
from llm.openai_service import OpenAIService
from mcp_servers.client import call_mcp_tool
from services.approval_service import ApprovalService
from llm.schemas import TechTicketDraft,TechTicketFixDraft

def tech_worker_node(state:State,db:Session)->State:
    llm=OpenAIService().llm
    rejection_reason=state.get("rejection_reason")
    target_id=state.get("target_id")
    prompt = f"""
    Analyze the user's technical request and create a technical support ticket.

    User request:
    {state["request"]}
    """

    if rejection_reason:
        prompt += f"""
        
    The previous Tech action was rejected.

    Rejection feedback:
    {rejection_reason}

    Revise the proposed technical ticket based on this feedback.
    """

    prompt += """
    
    Extract:
    - title
    - category
    - description
    - priority
    """
    response=llm.with_structured_output(TechTicketDraft).invoke(prompt)
    if rejection_reason and target_id:
        result = call_mcp_tool("update_ticket",{"ticket_id": str(target_id),"execution_id": str(state["execution_id"]),"title": response.title,"category": response.category,"description": response.description,"priority": response.priority},"tech")
    else:
        result=call_mcp_tool("create_ticket",{"execution_id":str(state["execution_id"]),"title":response.title,"category":response.category,"description":response.description,"priority":response.priority},"tech")
    tool_data=json.loads(result[0]["text"])
    approval_service=ApprovalService(db)
    ticket_id=UUID(tool_data["ticket_id"])
    approval_request=approval_service.create_pending(subject_type="tech_ticket",subject_id=UUID(tool_data["ticket_id"]),execution_id=state["execution_id"])
    return {**state,"current_node":"tech_worker","status":"running","output":tool_data,"subject_type":"tech_ticket","approval_request_id":approval_request.id,"subject_id":ticket_id,"target_id":ticket_id,"rejection_reason":None}
    
def tech_fix_worker_node(state:State,db:Session)->State:
    llm=OpenAIService().llm
    rejection_reason=state.get("rejection_reason")
    target_id=state.get("target_id")
    prompt = f"""
    Create a proposed technical fix for the existing support ticket.

    User request:
    {state["request"]}
    """

    if target_id:
        prompt += f"""
    Existing ticket ID:
    {target_id}

    Use this ticket ID.
    """
    else:
        prompt += """
    Extract the existing ticket ID from the user's request.
    """

    if rejection_reason:
        prompt += f"""
    The previous technical fix was rejected.

    Rejection feedback:
    {rejection_reason}

    Revise the proposed fix based on this feedback.
    """

    prompt += """
    Return:
    - ticket_id
    - proposed_fix
    """
    response=llm.with_structured_output(TechTicketFixDraft).invoke(prompt)
    ticket_id=target_id or response.ticket_id
    result=call_mcp_tool("create_ticket_fix",{"ticket_id":str(ticket_id),"execution_id":str(state["execution_id"]),"proposed_fix":response.proposed_fix},"tech")
    tool_data=json.loads(result[0]["text"])
    approval_service=ApprovalService(db)
    approval_request=approval_service.create_pending(subject_id=UUID(tool_data["fix_id"]),subject_type="tech_ticket_fix",execution_id=state["execution_id"])
    return{**state,"current_node":"tech_fix_worker","status":"running","output":tool_data,"subject_type":"tech_ticket_fix","approval_request_id":approval_request.id,"subject_id":UUID(tool_data["fix_id"]),"target_id":target_id}