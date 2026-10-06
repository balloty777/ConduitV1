from mcp.server.fastmcp import FastMCP
from database.database import get_session
from services.marketing_service import MarketingService
from mcp_servers.servers.marketing.schemas import DraftContentInput,DraftContentOutput,GetContentInput,GetContentOutput,UpdateContentInput,UpdateContentOutput

mcp=FastMCP("Marketing")

@mcp.tool()
def draft_content(data:DraftContentInput)->DraftContentOutput:
   """ Create a marketing content draft """
   with get_session() as db:
      service =MarketingService(db)
      content=service.draft_content(execution_id=data.execution_id,brief=data.brief,platform=data.platform,tone=data.tone,audience=data.audience,call_to_action=data.call_to_action)
      return DraftContentOutput(content_id=content.id,execution_id=content.execution_id,platform=content.platform,content=content.content,tone=content.tone,audience=content.audience,call_to_action=content.call_to_action,status=content.status)
   
@mcp.tool()
def get_content(data:GetContentInput)->GetContentOutput:
   """ Retrieve existing marketing content """
   with get_session() as db:
      service=MarketingService(db)
      content=service.get_content(content_id=data.content_id)
      return GetContentOutput(content_id=content.id,execution_id=content.execution_id,platform=content.platform,content=content.content,tone=content.tone,audience=content.audience,call_to_action=content.call_to_action,status=content.status,scheduled_at=content.scheduled_at)

@mcp.tool()
def update_content(data:UpdateContentInput)->UpdateContentOutput:
   """ Update existing marketing content """
   with get_session() as db:
      service=MarketingService(db)
      content=service.update_content(content_id=data.content_id,brief=data.brief,platform=data.platform,tone=data.tone,audience=data.audience,call_to_action=data.call_to_action)
      return UpdateContentOutput(content_id=content.id,execution_id=content.execution_id,platform=content.platform,content=content.content,tone=content.tone,audience=content.audience,call_to_action=content.call_to_action,status=content.status)


if __name__=="__main__":
   mcp.run()

