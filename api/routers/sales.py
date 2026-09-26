from uuid import UUID
from fastapi import APIRouter,Depends,status
from sqlalchemy.orm import Session
from api.dependencies import get_db
from services.sales_service import SalesService
from mcp_servers.servers.sales.schemas import CreateLeadInput,CreateLeadOutput,FollowUpLeadInput,FollowUpLeadOutput

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
    follow_up=service.follow_up_lead(lead_id=lead_id,execution_id=data.execution_id,message=data.message,channel=data.channel,scheduled_at=data.scheduled_at)
    return FollowUpLeadOutput(follow_up_id=follow_up.id,lead_id=follow_up.lead_id,execution_id=follow_up.execution_id,message=follow_up.message,channel=follow_up.channel,status=follow_up.status,scheduled_at=follow_up.scheduled_at)

@router.delete("/leads/follow-up/{follow_up_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_follow_up(follow_up_id:UUID,db:Session=Depends(get_db)):
    service=SalesService(db)
    service.delete_follow_up(follow_up_id)
    return None
