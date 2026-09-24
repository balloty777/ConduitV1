from sqlalchemy.orm import Session
from database.models.marketing_content import MarketingContent
from uuid import UUID

class MarketingContentRepository:
    def __init__(self,db:Session):
        self.db=db
    def create(self,marketing_content:MarketingContent)->MarketingContent:
        self.db.add(marketing_content)
        self.db.flush()
        return marketing_content
    def get_by_id(self,content_id:UUID)->MarketingContent|None:
        return self.db.get(MarketingContent,content_id)
    def get_by_execution_id(self,execution_id:UUID)->MarketingContent|None:
        return self.db.get(MarketingContent,execution_id)
    def update(self,marketing_content:MarketingContent)->MarketingContent:
        self.db.flush()
        return marketing_content
    def delete(self,content_id:UUID)->None:
        marketing_content=self.db.get(MarketingContent,content_id)
        if marketing_content is None:
            return None
        else:
            self.db.delete(marketing_content)
            self.db.flush()