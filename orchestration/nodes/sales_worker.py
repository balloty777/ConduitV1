from uuid import UUID
from sqlalchemy.orm import Session
from orchestration.state import State
from llm.openai_service import OpenAIService
from llm.schemas import SalesLeadDraft,SalesFollowUpDraft
from mcp_servers.client import call_mcp_tool
from services.approval_service import ApprovalService
import json

def sales_worker_node(state:State,db:Session)->State:
    llm=OpenAIService().llm
    rejection_reason = state.get("rejection_reason")
    prompt = f"""
    Extract the sales lead information from the user's request.

    User request:
    {state["request"]}
    """

    if rejection_reason:
        prompt += f"""
        
    The previous Sales action was rejected.

    Rejection feedback:
    {rejection_reason}

    Revise the proposed lead information based on this feedback.
    """

    prompt += """
    Return the structured fields required by SalesLeadDraft.
    """

    response=llm.with_structured_output(SalesLeadDraft).invoke(prompt)
    result=call_mcp_tool("create_lead",{"execution_id":str(state["execution_id"]),"name":response.name,"email":response.email,"phone":response.phone},"sales")
    tool_data=json.loads(result[0]["text"])
    approval_service=ApprovalService(db)
    approval_request=approval_service.create_pending(subject_type="sales_lead",subject_id=UUID(tool_data["lead_id"]),execution_id=state["execution_id"])
    return {**state,"current_node":"sales_worker","output":tool_data,"subject_type":"sales_lead","approval_request_id":approval_request.id,"subject_id":UUID(tool_data["lead_id"]),"status":"running"}

def sales_follow_up_worker_node(state:State,db:Session)->State:
    llm=OpenAIService().llm
    rejection_reason=state.get("rejection_reason")
    lead_id=state.get("subject_id")
    prompt = f"""
    Create a concise sales follow-up message for the existing lead.

    User request:
    {state["request"]}

    Lead ID:
    {lead_id}
    """

    if rejection_reason:
        prompt += f"""
        
    The previous follow-up was rejected.

    Rejection feedback:
    {rejection_reason}

    Revise the follow-up based on this feedback.
    """

    prompt += """
    
    Return:
    - message
    - channel
    - scheduled_at
    """
    response=llm.with_structured_output(SalesFollowUpDraft).invoke(prompt)
    result=call_mcp_tool("follow_up_lead",{"lead_id":str(lead_id),"execution_id":str(state["execution_id"]),"message":response.message,"channel":response.channel,"scheduled_at":response.scheduled_at},"sales")
    tool_data=json.loads(result[0]["text"])
    approval_service=ApprovalService(db)
    approval_request=approval_service.create_pending(subject_id=UUID(tool_data["follow_up_id"]),subject_type="sales_follow_up",execution_id=state["execution_id"])
    return {**state,"current_node":"sales_follow_up_worker","status":"running","output":tool_data,"subject_type":"sales_follow_up","approval_request_id":approval_request.id,"subject_id":UUID(tool_data["follow_up_id"])}