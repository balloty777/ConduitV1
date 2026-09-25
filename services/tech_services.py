from uuid import UUID
from sqlalchemy.orm import Session
from database.models.tech_ticket import TechTicket
from database.models.tech_fix import TechFix
from database.repositories.tech_ticket_repository import TechTicketRepository
from database.repositories.ticket_fix_repository import TechFixRepository
from exceptions.exceptions import ResourceAlreadyExist,ResourceNotFoundException,InvalidStateTransitionException
from datetime import datetime
from zoneinfo import ZoneInfo
IST = ZoneInfo("Asia/Kolkata")

class TechService:
    def __init__(self,db:Session):
        self.db=db
        self.techticketrepository=TechTicketRepository(db)
        self.techfixrepository=TechFixRepository(db)
    def create_ticket(self,execution_id:UUID,title:str,category:str,description:str,priority:str)->TechTicket:
        ticket=TechTicket(execution_id=execution_id,title=title,category=category,description=description,priority=priority)
        try:
            result=self.techticketrepository.create(ticket)
            self.db.commit()
            self.db.refresh(result)
            return result
        except Exception:
            self.db.rollback()
            raise
    def delete_ticket(self,ticket_id:UUID)->None:
        lead=self.techticketrepository.get_by_id(ticket_id)
        if lead is None:
            raise ResourceNotFoundException(f"Ticket for ticket id {ticket_id}  does not exists")
        try:
            self.techticketrepository.delete(ticket_id)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
    def create_ticket_fix(self,ticket_id:UUID,execution_id:UUID,proposed_fix:str)->TechFix:
        ticket=self.techticketrepository.get_by_id(ticket_id)
        if ticket is None:
            raise ResourceNotFoundException(f"Ticket id {ticket_id} does not exist")
        fix =TechFix(ticket_id=ticket_id,execution_id=execution_id,proposed_fix=proposed_fix)
        try:
            result=self.techfixrepository.create(fix)
            self.db.commit()
            self.db.refresh(result)
            return result
        except Exception:
            self.db.rollback()
            raise
    def delete_ticket_fix(self,ticket_id:UUID)->None:
        ticket=self.techfixrepository.get_by_id(ticket_id)
        if ticket is None:
            raise ResourceNotFoundException(f"Ticket id {ticket_id} does not exist")
        try:
            self.techfixrepository.delete(ticket.id)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
