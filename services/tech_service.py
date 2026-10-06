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
    def create_ticket(self,execution_id:UUID,title:str,category:str,description:str,proposed_fix:str,priority:str)->TechTicket:
        ticket=TechTicket(execution_id=execution_id,title=title,category=category,description=description,proposed_fix=proposed_fix,priority=priority)
        try:
            result=self.techticketrepository.create(ticket)
            self.db.commit()
            self.db.refresh(result)
            return result
        except Exception:
            self.db.rollback()
            raise
    def get_ticket(self,ticket_id:UUID)->TechTicket:
        ticket=self.techticketrepository.get_by_id(ticket_id=ticket_id)
        if ticket is None:
            raise ResourceNotFoundException(f"Ticket id {ticket_id} does not exist")
        return ticket
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
    def get_ticket_fix(self,fix_id:UUID)->TechFix:
        fix=self.techfixrepository.get_by_id(fix_id)
        if fix is None:
            raise ResourceNotFoundException(f"Ticket fix id {fix_id} does not exist")
        return fix
    def update_ticket(self,ticket_id:UUID,execution_id:UUID,title:str,category:str,description:str,proposed_fix:str,priority:str):
        ticket=self.techticketrepository.get_by_id(ticket_id)
        if ticket is None:
            raise ResourceNotFoundException(f"Ticket id {ticket_id} does not exist")
        ticket.execution_id=execution_id
        ticket.title=title
        ticket.category=category
        ticket.description=description
        ticket.proposed_fix=proposed_fix
        ticket.priority=priority
        try:
            self.techticketrepository.update(ticket)
            self.db.commit()
            self.db.refresh(ticket)
            return ticket
        except Exception:
            self.db.rollback()
            raise
    def update_ticket_fix(self,fix_id:UUID,execution_id:UUID,proposed_fix:str):
        fix=self.techfixrepository.get_by_id(fix_id)
        if fix is None:
            raise ResourceNotFoundException(f"Ticket fix id {fix_id} does not exist")
        fix.execution_id=execution_id
        fix.proposed_fix=proposed_fix
        try:
            self.techfixrepository.update(fix)
            self.db.commit()
            self.db.refresh(fix)
            return fix
        except Exception:
            self.db.rollback()
            raise
    def delete_ticket_fix(self,fix_id:UUID)->None:
        fix=self.techfixrepository.get_by_id(fix_id)
        if fix is None:
            raise ResourceNotFoundException(f"Fix id {fix_id} does not exist")
        try:
            self.techfixrepository.delete(fix_id)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
