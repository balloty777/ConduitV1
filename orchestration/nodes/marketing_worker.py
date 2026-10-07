from orchestration.state import State
from llm.openai_service import OpenAIService
from llm.schemas import MarketingDraft
from sqlalchemy.orm import Session
from services.approval_service import ApprovalService
from uuid import UUID
from services.marketing_service import MarketingService

def marketing_worker_node(state:State,db:Session)->State:
    llm=OpenAIService().llm
    rejection_reason = state.get("rejection_reason")
    prompt = f"""
    Create the actual publishable LinkedIn marketing post for this request.

    User request:
    {state["request"]}
    """

    if rejection_reason:
        prompt += f"""
    
    The previous draft was rejected.

    Rejection feedback:
    {rejection_reason}

    Revise the content based on this feedback.
    """

    prompt += """
    
    The `content` field must contain the finished LinkedIn post itself.
    Do not describe what the campaign should do.
    Do not provide instructions for another writer.
    Do not explain your approach.
    Write the actual post that could be published.

    Return the structured fields required by MarketingDraft.
    """
    response = llm.with_structured_output(MarketingDraft).invoke(prompt)
    target_id = state.get("target_id")
    service = MarketingService(db)
    if rejection_reason and target_id:
        content = service.update_content(content_id=target_id, brief=response.content, platform=response.platform, tone=response.tone, audience=response.audience, call_to_action=response.call_to_action)
    else:
        content = service.draft_content(execution_id=state["execution_id"], brief=response.content, platform=response.platform, tone=response.tone, audience=response.audience, call_to_action=response.call_to_action)
    tool_data = {"content_id": str(content.id), "execution_id": str(content.execution_id), "platform": content.platform, "content": content.content, "tone": content.tone, "audience": content.audience, "call_to_action": content.call_to_action, "status": content.status}
    approval_service = ApprovalService(db)
    approval_request = approval_service.create_pending(subject_type="marketing_content",subject_id=UUID(tool_data["content_id"]),execution_id=state["execution_id"])
    return {**state,"current_node": "marketing_worker","status": "running","output": tool_data,"subject_type": "marketing_content","approval_request_id": approval_request.id,"subject_id": UUID(tool_data["content_id"]),"target_id": UUID(tool_data["content_id"])}
