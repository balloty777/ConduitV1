from uuid import UUID
from fastapi import APIRouter,Depends,status
from sqlalchemy.orm import Session
from api.dependencies import get_db
from services.tech_service import TechService
from mcp_servers.servers.tech.schemas import CreateTicketInput,CreateTicketOutput,TicketFixInput,TicketFixOutput

router = APIRouter(prefix="/tech",tags=["Tech"])

@router.post("/tickets",response_model=CreateTicketOutput,status_code=status.HTTP_201_CREATED)
def create_ticket(data:CreateTicketInput,db:Session=Depends(get_db)):
    service=TechService(db)
    ticket=service.create_ticket(execution_id=data.execution_id,title=data.title,category=data.category,description=data.description,proposed_fix=data.proposed_fix,priority=data.priority)
    return CreateTicketOutput(ticket_id=ticket.id,execution_id=ticket.execution_id,title=ticket.title,category=ticket.category,description=ticket.description,proposed_fix=ticket.proposed_fix,priority=ticket.priority,status=ticket.status)

@router.delete("/tickets/{ticket_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id:UUID,db:Session=Depends(get_db)):
    service=TechService(db)
    service.delete_ticket(ticket_id)
    return None

@router.post("/tickets/{ticket_id}/fix",response_model=TicketFixOutput,status_code=status.HTTP_201_CREATED)
def create_ticket_fix(ticket_id:UUID,data:TicketFixInput,db:Session=Depends(get_db)):
    service=TechService(db)
    fix=service.create_ticket_fix(ticket_id=ticket_id,execution_id=data.execution_id,proposed_fix=data.proposed_fix)
    return TicketFixOutput(fix_id=fix.id,ticket_id=fix.ticket_id,execution_id=fix.execution_id,proposed_fix=fix.proposed_fix,status=fix.status)

@router.delete("/tickets/fix/{fix_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket_fix(fix_id:UUID,db:Session=Depends(get_db)):
    service=TechService(db)
    service.delete_ticket_fix(fix_id)
    return None
