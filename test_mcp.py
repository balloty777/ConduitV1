import asyncio
from mcp_servers.client import get_mcp_client


async def main():
    client = get_mcp_client()

    tools = await client.get_tools(server_name="marketing")
    draft_tool = next(tool for tool in tools if tool.name == "draft_content")

    result = await draft_tool.ainvoke({
        "data": {
            "execution_id": "adbdf2c4-1ae4-4a64-9b9e-4585db0e839f",
            "brief": "Create a LinkedIn campaign for a new product",
            "platform": "linkedin",
            "tone": "confident and energetic",
            "audience": "early adopters",
            "call_to_action": "Discover it now",
        }
    })


    print(result)


asyncio.run(main())