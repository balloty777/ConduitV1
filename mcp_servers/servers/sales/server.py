from mcp.server.fastmcp import FastMCP
from database.database import get_session
from services.sales_service import SalesService
from mcp_servers.servers.sales.schemas import CreateLeadInput,CreateLeadOutput,DeleteFollowUpInput,DeleteFollowUpOutput,DeleteLeadInput,DeleteLeadOutput,FollowUpLeadInput,FollowUpLeadOutput

mcp=FastMCP("sales")

@mcp.tool()
def create_lead(data:CreateLeadInput)->CreateLeadOutput:
    """ Create a new sales lead """
    with get_session() as db:
        service=SalesService(db)
        lead=service.create_lead(execution_id=data.execution_id,name=data.name,email=data.email,phone=data.phone)
        return CreateLeadOutput(lead_id=lead.id,execution_id=lead.execution_id,name=lead.name,email=lead.email,phone=lead.phone,status=lead.status)

@mcp.tool()
def delete_lead(data:DeleteLeadInput)->DeleteLeadOutput:
    """ Delete a existing sales lead """
    with get_session() as db:
        service=SalesService(db)
        service.delete_lead(data.lead_id)
        return DeleteLeadOutput(lead_id=data.lead_id,deleted=True)

@mcp.tool()
def follow_up_lead(data:FollowUpLeadInput)->FollowUpLeadOutput:
    """ Create a follow up for sales lead """
    with get_session() as db:
        service=SalesService(db)
        follow_up=service.follow_up_lead(lead_id=data.lead_id,execution_id=data.execution_id,message=data.message,channel=data.channel,scheduled_at=data.scheduled_at)
        return FollowUpLeadOutput(follow_up_id=follow_up.id,lead_id=follow_up.lead_id,execution_id=follow_up.execution_id,message=follow_up.message,channel=follow_up.channel,status=follow_up.status,scheduled_at=follow_up.scheduled_at)

@mcp.tool()
def delete_follow_up(data:DeleteFollowUpInput)->DeleteFollowUpOutput:
    """ Delete an existing sales follow-up """
    with get_session() as db:
        service=SalesService(db)
        service.delete_follow_up(follow_up_id=data.follow_up_id)
        return DeleteFollowUpOutput(follow_up_id=data.follow_up_id,deleted=True)

if __name__=="__main__":
    mcp.run()