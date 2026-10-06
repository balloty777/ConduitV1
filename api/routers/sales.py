from uuid import UUID
from fastapi import APIRouter,Depends,status
from sqlalchemy.orm import Session
from api.dependencies import get_db
from exceptions.exceptions import ResourceAlreadyExist,ResourceNotFoundException,InvalidStateTransitionException
from services.sales_service import SalesService
from services.approval_service import ApprovalService
from services.workflow_execution_service import WorkflowExecutionService
from mcp_servers.servers.sales.schemas import CreateLeadInput,CreateLeadOutput,FollowUpLeadInput,FollowUpLeadOutput,ScheduleFollowUpInput,ScheduleFollowUpOutput

router=APIRouter(  prefix="/sales",tags=["Sales"])

@router.post("/leads",response_model=CreateLeadOutput,status_code=status.HTTP_201_CREATED)
def create_lead(data:CreateLeadInput,db:Session=Depends(get_db)):
    service=SalesService(db)
    lead=service.create_lead(
        execution_id=data.execution_id,
        name=data.name,
        email=data.email,
        phone=data.phone
    )
    return CreateLeadOutput(lead_id=lead.id,execution_id=lead.execution_id,name=lead.name,email=lead.email,phone=lead.phone,status=lead.status)

@router.delete("/leads/{lead_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id:UUID,db:Session=Depends(get_db)):
    service=SalesService(db)
    service.delete_lead(lead_id)
    return None

@router.post("/leads/{lead_id}/follow-up",response_model=FollowUpLeadOutput,status_code=status.HTTP_201_CREATED)
def follow_up_lead(lead_id:UUID,data:FollowUpLeadInput,db:Session=Depends(get_db)):
    service=SalesService(db)
    follow_up=service.follow_up_lead(lead_id=lead_id,execution_id=data.execution_id,message=data.message,channel=data.channel)
    return FollowUpLeadOutput(follow_up_id=follow_up.id,lead_id=follow_up.lead_id,execution_id=follow_up.execution_id,message=follow_up.message,channel=follow_up.channel,status=follow_up.status)

@router.post("/leads/follow-up/{follow_up_id}/schedule",response_model=ScheduleFollowUpOutput)
def schedule_follow_up(follow_up_id:UUID,data:ScheduleFollowUpInput,db:Session=Depends(get_db)):
    approval_service=ApprovalService(db)
    sales_service=SalesService(db)
    workflow_service=WorkflowExecutionService(db)
    approval_request=approval_service.get_by_subject_id(subject_id=follow_up_id)
    if approval_request.subject_type != "sales_follow_up":
        raise InvalidStateTransitionException("This approval request does not belong to a sales follow-up")
    if approval_request.status!="approved":
        raise InvalidStateTransitionException("Sales follow-up must be approved before scheduling")
    follow_up=sales_service.schedule_follow_up(follow_up_id=follow_up_id,scheduled_at=data.scheduled_at)
    workflow_service.complete_execution(execution_id=follow_up.execution_id,result={"follow_up_id": str(follow_up.id),"status": follow_up.status,"scheduled_at": follow_up.scheduled_at.isoformat()})
    return ScheduleFollowUpOutput(follow_up_id=follow_up.id,lead_id=follow_up.lead_id,execution_id=follow_up.execution_id,message=follow_up.message,channel=follow_up.channel,status=follow_up.status,scheduled_at=follow_up.scheduled_at)

@router.delete("/leads/follow-up/{follow_up_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_follow_up(follow_up_id:UUID,db:Session=Depends(get_db)):
    service=SalesService(db)
    service.delete_follow_up(follow_up_id)
    return None
