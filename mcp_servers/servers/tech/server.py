from mcp.server.fastmcp import FastMCP
from database.database import get_session
from services.tech_service import TechService
from mcp_servers.servers.tech.schemas import CreateTicketInput,CreateTicketOutput,TicketFixInput,TicketFixOutput,UpdateTicketInput,UpdateTicketOutput,UpdateTicketFixInput,UpdateTicketFixOutput,GetTicketInput,GetTicketOutput,GetTicketFixInput,GetTicketFixOutput

mcp=FastMCP("tech") 

@mcp.tool()
def create_ticket(data:CreateTicketInput)->CreateTicketOutput:
    """ Create a technical support ticket """
    with get_session() as db:
        service=TechService(db)
        ticket=service.create_ticket(execution_id=data.execution_id,title=data.title,category=data.category,description=data.description,proposed_fix=data.proposed_fix,priority=data.priority)
        return CreateTicketOutput(ticket_id=ticket.id,execution_id=ticket.execution_id,title=ticket.title,category=ticket.category,description=ticket.description,proposed_fix=ticket.proposed_fix,priority=ticket.priority,status=ticket.status)
    
@mcp.tool()
def create_ticket_fix(data:TicketFixInput)->TicketFixOutput:
    """ Create a proposed fix for a technical ticket """
    with get_session() as db:
        service=TechService(db)
        fix=service.create_ticket_fix(ticket_id=data.ticket_id,execution_id=data.execution_id,proposed_fix=data.proposed_fix)
        return TicketFixOutput(fix_id=fix.id,ticket_id=fix.ticket_id,execution_id=fix.execution_id,proposed_fix=fix.proposed_fix,status=fix.status)
        
@mcp.tool()
def update_ticket(data:UpdateTicketInput)->UpdateTicketOutput:
    """ Update an existing technical support ticket """
    with get_session() as db:
        service=TechService(db)
        ticket = service.update_ticket(ticket_id=data.ticket_id,execution_id=data.execution_id,title=data.title,category=data.category,description=data.description,proposed_fix=data.proposed_fix,priority=data.priority)
        return UpdateTicketOutput(ticket_id=ticket.id,execution_id=ticket.execution_id,title=ticket.title,category=ticket.category,description=ticket.description,proposed_fix=ticket.proposed_fix,priority=ticket.priority,status=ticket.status)
    
@mcp.tool()
def update_ticket_fix(data:UpdateTicketFixInput)->UpdateTicketFixOutput:
    """ Update an existing proposed technical fix """
    with get_session() as db:
        service=TechService(db)
        fix=service.update_ticket_fix(fix_id=data.fix_id,execution_id=data.execution_id,proposed_fix=data.proposed_fix)
        return UpdateTicketFixOutput(fix_id=fix.id,ticket_id=fix.ticket_id,execution_id=fix.execution_id,proposed_fix=fix.proposed_fix,status=fix.status)
@mcp.tool()
def get_ticket(data:GetTicketInput)->GetTicketOutput:
    """ Get an existing technical support ticket """
    with get_session() as db:
        service=TechService(db)
        ticket=service.get_ticket(ticket_id=data.ticket_id)
        return GetTicketOutput(ticket_id=ticket.id,execution_id=ticket.execution_id,title=ticket.title,category=ticket.category,description=ticket.description,proposed_fix=ticket.proposed_fix,priority=ticket.priority,status=ticket.status)

@mcp.tool()
def get_ticket_fix(data:GetTicketFixInput)->GetTicketFixOutput:
    """Get an existing proposed fix for a technical ticket"""
    with get_session() as db:
        service=TechService(db)
        fix=service.get_ticket_fix(fix_id=data.fix_id)
        return GetTicketFixOutput(fix_id=fix.id,ticket_id=fix.ticket_id,execution_id=fix.execution_id,proposed_fix=fix.proposed_fix,status=fix.status)

if __name__=="__main__":
    mcp.run()
