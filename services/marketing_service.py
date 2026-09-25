from uuid import UUID
from sqlalchemy.orm import Session
from database.models.marketing_content import MarketingContent
from database.repositories.marketing_content_repository import MarketingContentRepository
from exceptions.exceptions import ResourceAlreadyExist,ResourceNotFoundException,InvalidStateTransitionException
from datetime import datetime
from zoneinfo import ZoneInfo
IST = ZoneInfo("Asia/Kolkata")
class MarketingService:
    def __init__(self,db:Session):
        self.db=db
        self.repository=MarketingContentRepository(db)
    def draft_content(self,execution_id:UUID,brief:str,platform:str,tone:str,audience:str,call_to_action:str|None=None)->MarketingContent:
        marketing_content=MarketingContent(
            execution_id=execution_id,
            content=brief,
            platform=platform,
            tone=tone,
            audience=audience,
            call_to_action=call_to_action,
            status="draft"
        )
        try:
            result= self.repository.create(marketing_content=marketing_content)
            self.db.commit()
            self.db.refresh(result)
            return result
        except Exception:
            self.db.rollback()
            raise
    def get_content(self,content_id:UUID)->MarketingContent:
        content= self.repository.get_by_id(content_id)
        if content is None:
            raise ResourceNotFoundException(f"Marketing content for {content_id} does not exist")
        return content
    def update_content(self,content_id:UUID,brief:str,platform:str,tone:str,audience:str,call_to_action:str|None=None)->MarketingContent:
        marketing_content=self.get_content(content_id)
        if marketing_content.status != "draft":
            raise InvalidStateTransitionException(f"Cannot update content with status {marketing_content.status}")
        marketing_content.content=brief
        marketing_content.platform=platform
        marketing_content.tone=tone
        marketing_content.audience=audience
        marketing_content.call_to_action=call_to_action
        try:
            result= self.repository.update(marketing_content)
            self.db.commit()
            self.db.refresh(result)
            return result
        except Exception:
            self.db.rollback()
            raise
    def schedule_content(self,content_id:UUID,scheduled_at:datetime)->MarketingContent:
        marketing_content=self.get_content(content_id)
        if scheduled_at<=datetime.now(IST):
            raise InvalidStateTransitionException("The content can not be scheduled for the past")
        if marketing_content.status!="draft":
            raise InvalidStateTransitionException(f"Cannot schedule content with status :  {marketing_content.status}")
        marketing_content.scheduled_at=scheduled_at
        marketing_content.status="pending_approval"
        try:
            result= self.repository.update(marketing_content)
            self.db.commit()
            self.db.refresh(result)
            return result
        except Exception:
            self.db.rollback()
            raise
    def delete_content(self,content_id:UUID)->None:
        marketing_content=self.get_content(content_id=content_id)
        try:
            self.repository.delete(marketing_content.id)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise