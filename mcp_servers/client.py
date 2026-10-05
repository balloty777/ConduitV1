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
            },
            "sales":{
                "command":sys.executable,
                "args":["-m","mcp_servers.servers.sales.server"],
                "transport":"stdio"
            },
            "tech":{
                "command": sys.executable,
                "args": ["-m", "mcp_servers.servers.tech.server"],
                "transport": "stdio",
            }
        }
    )

def call_mcp_tool(tool_name:str,arguments:dict,server_name:str):
    async def _call():
        client=get_mcp_client()
        tools=await client.get_tools(server_name=server_name)
        tool=next(tool for tool in tools if tool.name==tool_name)
        return await tool.ainvoke({"data":arguments})
    return asyncio.run(_call())