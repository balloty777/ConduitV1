from uuid import UUID
from sqlalchemy.orm import Session
from database.models.sales_follow_ups import SalesFollowUp

class SalesFollowUpsRepository:
    def __init__(self,db:Session):
        self.db=db
    def create(self,follow_up:SalesFollowUp)->SalesFollowUp:
        self.db.add(follow_up)
        self.db.flush()
        return follow_up
    def get_by_id(self,follow_up_id:UUID)->SalesFollowUp|None:
        return self.db.get(SalesFollowUp,follow_up_id)
    def update(self,follow_up)->SalesFollowUp:
        self.db.flush()
        return follow_up
    def delete(self,follow_up_id)->None:
        follow_up=self.db.get(SalesFollowUp,follow_up_id)
        if follow_up is  None:
            return None
        else:
            self.db.delete(follow_up)
            self.db.flush()