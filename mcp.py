# The imports

from dotenv import load_dotenv
from agents import Agent, Runner, trace
import os

load_dotenv(override=True)

async def main():
    fetch_params = MCPServerStdioParams(command="uvx", args=["mcp-server-fetch"])
    async with MCPServerStdio(params=fetch_params, client_session_timeout_seconds=60) as server:
        fetch_server_tools = await server.list_tools()

    print("Fetch server tools:", fetch_server_tools)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())