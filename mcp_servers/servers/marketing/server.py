from uuid import uuid4
from schemas import DraftContentInput,DraftContentOutput,GetContentInput,GetContentOutput,ScheduleContentInput,ScheduleContentOutput
from mcp.server.fastmcp import FastMCP
mcp=FastMCP("marketing")

@mcp.tool()
def draft_content(data:DraftContentInput)->DraftContentOutput:
     """Create a marketing content draft from a content brief."""
     return DraftContentOutput(
        content_id=uuid4(),
        platform=data.platform,
        content=f"Content for {data.platform} is :\n {data.brief}",
        status="draft"
     )

def get_content(data:GetContentInput)->GetContentOutput:
   """Retrieve an existing marketing content draft."""
if __name__ == "__main__":
    mcp.run()
