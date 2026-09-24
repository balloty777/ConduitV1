from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from database.models.marketing_content import MarketingContent
from database.repositories.marketing_content_repository import MarketingContentRepository
from exceptions.exceptions import ConduitException,ResourceAlreadyExist,ResourceNotFoundException
class MarketingService:
    def __init__(self,db:Session):
        self.db=db
        self.repository=MarketingContentRepository(db)
    def draft_content(self,execution_id:UUID,brief:str,platform:str,tone:str,audience:str,call_to_action:str|None=None)->MarketingContent:
        marketing_content=MarketingContent(
            execution_id=execution_id,
            platform=platform,
            content=brief,
            tone=tone,
            audience=audience,
            call_to_action=call_to_action,
            status="draft"
        )
        return self.repository.create(marketing_content=marketing_content)
    def get_content(self,content_id:UUID)->MarketingContent:
        content= self.repository.get_by_id(content_id)
        if content is None:
            raise ResourceNotFoundException(f"Marketing content for {content_id} does not exist")
        return content
    def update_content(self,id:UUID,execution_id:UUID,brief:str,platform:str,tone:str,audience:str,call_to_action:str|None=None)->MarketingContent:
        marketing_content=MarketingContent(
            execution_id=execution_id,
            platform=platform,
            content=brief,
            tone=tone,
            audience=audience,
            call_to_action=call_to_action,
            status="draft"
        )
        self.repository.update(marketing_content)