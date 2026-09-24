from uuid import UUID
from sqlalchemy.orm import Session
from database.models.tech_ticket import TechTicket

class TechTicketRepository:
    def __init__(self,db:Session):
        self.db=db
    def create(self,ticket:TechTicket)->TechTicket:
        self.db.add(ticket)
        self.db.flush()
        return ticket
    def get_by_id(self,ticket_id:UUID)->TechTicket|None:
        return self.db.get(TechTicket,ticket_id)
    def update(self,ticket:TechTicket)->TechTicket:
        self.db.flush()
        return ticket
    def delete(self,ticket_id:UUID)->None:
        ticket=self.db.get(TechTicket,ticket_id)
        if ticket is None:
            return None
        else:
            self.db.delete(ticket)
            self.db.flush()