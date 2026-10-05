from uuid import UUID
import json
from sqlalchemy.orm import Session
from orchestration.state import State
from llm.openai_service import OpenAIService
from mcp_servers.client import call_mcp_tool
from services.approval_service import ApprovalService
from llm.schemas import TechTicketDraft

def tech_worker_node(state:State,db:Session)->State:
    llm=OpenAIService().llm
    rejection_reason=state.get("rejection_reason")
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
    result=call_mcp_tool("create_ticket",{"execution_id":str(state["execution_id"]),"title":response.title,"category":response.category,"description":response.description,"priority":response.priority},"tech")
    tool_data=json.loads(result[0]["text"])
    approval_service=ApprovalService(db)
    approval_request=approval_service.create_pending(subject_type="tech_ticket",subject_id=UUID(tool_data["ticket_id"]),execution_id=state["execution_id"])
    return {**state,"current_node":"tech_worker","status":"running","output":tool_data,"subject_type":"tech_ticket","approval_request_id":approval_request.id,"subject_id":UUID(tool_data["ticket_id"])}
    
