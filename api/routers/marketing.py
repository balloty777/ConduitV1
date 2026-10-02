from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from api.dependencies import get_db
from mcp_servers.servers.marketing.schemas import DraftContentOutput,DraftContentInput,GetContentInput,GetContentOutput,ScheduleContentInput,ScheduleContentOutput,UpdateContentInput,UpdateContentOutput,DeleteContentInput,DeleteContentOutput,ApproveContentInput,ApproveContentOutput,RejectContentInput
from services.marketing_service import MarketingService
from services.workflow_execution_service import WorkflowExecutionService
from services.approval_service import ApprovalService
from exceptions.exceptions import InvalidStateTransitionException
from langgraph.types import Command
from orchestration.graph import build_graph 
from uuid import UUID
from datetime import datetime
router= APIRouter(prefix="/marketing", tags=["Marketing"])

@router.post("/content/draft",response_model=DraftContentOutput)
def draft_content(data:DraftContentInput,db:Session= Depends(get_db)):
    service=MarketingService(db)
    result=service.draft_content(
        execution_id=data.execution_id,
        brief=data.brief,
        platform=data.platform,
        tone=data.tone,
        audience=data.audience,
        call_to_action=data.call_to_action
    )
    return DraftContentOutput(content_id=result.id,execution_id=result.execution_id,platform=result.platform,content=result.content,tone=result.tone,audience=result.audience,call_to_action=result.call_to_action,status=result.status)

@router.get("/content/{content_id}",response_model=GetContentOutput)
def get_content(content_id:UUID,db:Session=Depends(get_db)):
    service=MarketingService(db)
    result=service.get_content(content_id)
    return GetContentOutput(content_id=result.id,execution_id=result.execution_id,platform=result.platform,content=result.content,tone=result.tone,audience=result.audience,call_to_action=result.call_to_action,status=result.status,scheduled_at=result.scheduled_at)

@router.put("/content/{content_id}", response_model=UpdateContentOutput)
def update_content(content_id:UUID,data:UpdateContentInput,db:Session=Depends(get_db))->UpdateContentOutput:
    service=MarketingService(db)
    result=service.update_content(content_id=content_id,brief=data.brief,platform=data.platform,tone=data.tone,audience=data.audience,call_to_action=data.call_to_action)
    return UpdateContentOutput(content_id=result.id,execution_id=result.execution_id,platform=result.platform,content=result.content,tone=result.tone,audience=result.audience,call_to_action=result.call_to_action,status=result.status)

@router.post( "/content/{content_id}/schedule",response_model=ScheduleContentOutput)
def schedule_content(content_id:UUID,data:ScheduleContentInput,db:Session=Depends(get_db)):
    service=MarketingService(db)
    result=service.schedule_content(content_id=content_id,scheduled_at=data.scheduled_at)
    return ScheduleContentOutput(content_id=result.id,execution_id=result.execution_id,platform=result.platform,status=result.status,scheduled_at=result.scheduled_at)

@router.post("/content/{content_id}/approve",response_model=ApproveContentOutput)
def approve_content(content_id:UUID,data:ApproveContentInput,user_id:UUID,db:Session=Depends(get_db)):
    approval_service=ApprovalService(db)
    marketing_service=MarketingService(db)
    approval_request=approval_service.get_pending_by_subject_id(subject_id=content_id)
    workflow_service=WorkflowExecutionService(db)
    result=marketing_service.schedule_content(content_id=content_id,scheduled_at=data.scheduled_at,commit=False)
    approval_service.approve(approval_request_id=approval_request.id,decided_by=user_id,commit=False)
    db.commit()
    with build_graph(db) as graph:
        final_state=graph.invoke(Command(resume={"decision":"approved"}),config={"configurable":{"thread_id":str(approval_request.execution_id)}})
    workflow_service.complete_execution(execution_id=approval_request.execution_id,result=final_state)
    return ApproveContentOutput(content_id=result.id,execution_id=result.execution_id,platform=result.platform,status=result.status,scheduled_at=result.scheduled_at)

@router.post("/content/{content_id}/reject")
def reject_content(content_id:UUID,data:RejectContentInput,user_id:UUID,db:Session=Depends(get_db)):
    approval_service=ApprovalService(db)
    approval_request=approval_service.get_pending_by_subject_id(subject_id=content_id)
    rejection=approval_service.reject(approval_request_id=approval_request.id,decided_by=user_id,reason=data.reason)
    with build_graph(db) as graph:
        result=graph.invoke(Command(resume={"decision":"rejected","reason":data.reason}),config={"configurable":{"thread_id":str(approval_request.execution_id)}})
    return {"content_id":result["subject_id"],"approval_request_id":result["approval_request_id"],"status":"pending","reason":rejection.reason}

@router.delete("/content/{content_id}", status_code=204)
def delete_content(content_id:UUID,db:Session=Depends(get_db)):
    service=MarketingService(db)
    service.delete_content(content_id=content_id)
