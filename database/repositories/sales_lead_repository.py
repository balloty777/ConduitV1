from uuid import UUID
from sqlalchemy.orm import Session
from database.models.sales_lead import SalesLead

class SalesLeadRepository:
    def __init__(self,db:Session):
        self.db=db
    def create(self,sales_lead:SalesLead)->SalesLead:
        self.db.add(sales_lead)
        self.db.flush()
        return sales_lead
    def get_by_id(self,lead_id:UUID)->SalesLead|None:
        return self.db.get(SalesLead,lead_id)
    def get_by_execution_id(self,execution_id:UUID)->SalesLead|None:
        return self.db.get(SalesLead,execution_id)
    def get_by_email(self,email:str)->SalesLead|None:
        return self.db.query(SalesLead).filter(SalesLead.email==email).first()
    def update(self,sales_lead:SalesLead)->SalesLead:
        self.db.flush()
        return sales_lead
    def delete(self,lead_id:UUID)->None:
        sales_lead=self.db.get(SalesLead,lead_id)
        if sales_lead is None:
            return None
        else:
            self.db.delete(sales_lead)
            self.db.flush()
        