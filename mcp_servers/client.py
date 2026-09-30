import sys
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

def get_mcp_client()->MultiServerMCPClient:
    return MultiServerMCPClient(
        {
            "marketing":{
                "command":sys.executable,
                "args":["-m", "mcp_servers.servers.marketing.server"],
                "transport":"stdio"
            }
        }
    )

def call_mcp_tool(tool_name:str,arguments:dict):
    async def _call():
        client=get_mcp_client()
        tools=await client.get_tools(server_name="marketing")
        tool=next(tool for tool in tools if tool.name==tool_name)
        return await tool.ainvoke({"data":arguments})
    return asyncio.run(_call())