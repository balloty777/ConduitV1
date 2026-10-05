from uuid import UUID
from sqlalchemy.orm import Session
from database.models.sales_lead import SalesLead
from database.models.sales_follow_ups import SalesFollowUp
from database.repositories.sales_lead_repository import SalesLeadRepository
from database.repositories.sales_follow_ups_repository import SalesFollowUpsRepository
from exceptions.exceptions import ResourceAlreadyExist,ResourceNotFoundException,InvalidStateTransitionException
from datetime import datetime
from zoneinfo import ZoneInfo
IST = ZoneInfo("Asia/Kolkata")

class SalesService:
    def __init__(self,db:Session):
        self.db=db
        self.salesleadrepository=SalesLeadRepository(db)
        self.salesfollowuprepository=SalesFollowUpsRepository(db)
    def create_lead(self,execution_id:UUID,name:str,email:str,phone:str|None=None)->SalesLead:
        lead=self.salesleadrepository.get_by_email(email)
        if lead is not None:
            raise ResourceAlreadyExist(f"Lead with {lead.email} is already present")
        sales_lead=SalesLead(execution_id=execution_id,name=name,email=email,phone=phone)
        try:
            result=self.salesleadrepository.create(sales_lead)
            self.db.commit()
            self.db.refresh(result)
            return result
        except Exception:
            self.db.rollback()
            raise
    def update_lead(self,lead_id:UUID,execution_id:UUID,name:str,email:str,phone:str|None=None)->SalesLead:
        lead=self.salesleadrepository.get_by_id(lead_id)
        if lead is None:
            raise ResourceNotFoundException(f"Lead id {lead_id} does not exist")
        existing_lead=self.salesleadrepository.get_by_email(email)
        if existing_lead is not None and existing_lead.id !=lead_id:
            raise ResourceAlreadyExist(f"Lead with {existing_lead.email} is already present")
        lead.execution_id=execution_id
        lead.name=name
        lead.email=email
        if phone is not None:
            lead.phone=phone
        try:
            self.salesleadrepository.update(lead)
            self.db.commit()
            self.db.refresh(lead)
            return lead
        except Exception:
            self.db.rollback()
            raise
    def delete_lead(self,lead_id:UUID)->None:
        lead=self.salesleadrepository.get_by_id(lead_id)
        if lead is None:
            raise ResourceNotFoundException(f"Lead id {lead_id} does not eixst")
        try :
            self.salesleadrepository.delete(lead.id)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
    def follow_up_lead(self,lead_id:UUID,execution_id:UUID,message:str,channel:str,scheduled_at:datetime|None=None)->SalesFollowUp:
        lead=self.salesleadrepository.get_by_id(lead_id)
        if lead is None:
            raise ResourceNotFoundException(f"Lead id {lead_id} does not exist")
        follow_up=SalesFollowUp(
            lead_id=lead_id,
            execution_id=execution_id,
            message=message,
            channel=channel,
            scheduled_at=scheduled_at
        )
        try:
            result=self.salesfollowuprepository.create(follow_up)
            self.db.commit()
            self.db.refresh(result)
            return result
        except Exception:
            self.db.rollback()
            raise
    def delete_follow_up(self,follow_up_id:UUID)->None:
        follow_up=self.salesfollowuprepository.get_by_id(follow_up_id)
        if follow_up is None:
            raise ResourceNotFoundException(f"Follow up id {follow_up_id} does not exist")
        try:
            self.salesfollowuprepository.delete(follow_up_id)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise