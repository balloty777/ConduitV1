from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from api.dependencies import get_db
from mcp_servers.servers.marketing.schemas import DraftContentOutput,DraftContentInput,GetContentInput,GetContentOutput,ScheduleContentInput,ScheduleContentOutput
from services.marketing_service import MarketingService
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
    return DraftContentOutput(
        content_id=result.id,
        platform=result.platform,
        content=result.content,
        status=result.status
    )

@router.get("/content/{content_id}",response_model=GetContentOutput)
def get_content(content_id:UUID,db:Session=Depends(get_db)):
    service=MarketingService(db)
    result=service.get_content(content_id)
    return GetContentOutput(
        content_id=result.id,
        platform=result.platform,
        content=result.content,
        status=result.status
        )
@router.post( "/content/{content_id}/schedule",response_model=ScheduleContentOutput)
def schedule_content(content_id:UUID,data:ScheduleContentInput,db:Session=Depends(get_db)):
    service=MarketingService(db)
    result=service.schedule_content(content_id=content_id,scheduled_at=data.scheduled_at)
    return ScheduleContentOutput(content_id=result.id,platform=result.platform,status=result.status,scheduled_at=result.scheduled_at)

@router.delete("/content/{content_id}", status_code=204)
def delete_content(content_id:UUID,db:Session=Depends(get_db)):
    service=MarketingService(db)
    service.delete_content(content_id=content_id)
