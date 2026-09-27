from mcp.server.fastmcp import FastMCP
from database.database import get_session
from services.tech_service import TechService
from mcp_servers.servers.tech.schemas import CreateTicketInput,CreateTicketOutput,DeleteTicketInput,DeleteTicketOutput,DeleteTicketFixInput,DeleteTicketFixOutput,TicketFixInput,TicketFixOutput

mcp=FastMCP("tech")

@mcp.tool()
def create_ticket(data:CreateTicketInput)->CreateTicketOutput:
    """ Create a technical support ticket """
    with get_session() as db:
        service=TechService(db)
        ticket=service.create_ticket(execution_id=data.execution_id,title=data.title,category=data.category,description=data.description,priority=data.priority)
        return CreateTicketOutput(ticket_id=ticket.id,execution_id=ticket.execution_id,title=ticket.title,category=ticket.category,description=ticket.description,priority=ticket.priority,status=ticket.status)

@mcp.tool()
def delete_ticket(data:DeleteTicketInput)->DeleteTicketOutput:
    """ Delete a technical support ticket """
    with get_session() as db:
        service=TechService(db)
        service.delete_ticket(ticket_id=data.ticket_id)
        return DeleteTicketOutput(ticket_id=data.ticket_id,deleted=True)
    
@mcp.tool()
def create_ticket_fix(data:TicketFixInput)->TicketFixOutput:
    """ Create a proposed fix for a technical ticket """
    with get_session() as db:
        service=TechService(db)
        fix=service.create_ticket_fix(ticket_id=data.ticket_id,execution_id=data.execution_id,proposed_fix=data.proposed_fix)
        return TicketFixOutput(fix_id=fix.id,ticket_id=fix.ticket_id,execution_id=fix.execution_id,proposed_fix=fix.proposed_fix,status=fix.status)

@mcp.tool()
def delete_ticket_fix(data:DeleteTicketFixInput)->DeleteTicketFixOutput:
    """ Delete a proposed ticket fix """
    with get_session() as db:
        service=TechService(db)
        service.delete_ticket_fix(ticket_id=data.fix_id)
        return DeleteTicketFixOutput(fix_id=data.fix_id,deleted=True)
        
