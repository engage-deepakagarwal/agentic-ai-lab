# The imports

from dotenv import load_dotenv
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
import os

async def list_tools_from_mcp_server():
    # Load environment variables from .env file
    # Make sure the mcp-server-fetch is running using `uvx mcp-server-fetch`
    load_dotenv(override=True)
    
    # Set up MCP server parameters
    fetch_mcp_server = StdioServerParams(command="uvx", args=["mcp-server-fetch"])
    
    # Initialize the MCP workbench
    async with McpWorkbench(server_params=fetch_mcp_server) as workbench:
        # List tools from the MCP server
        tools = await workbench.list_tools()
        return tools

async def main():
    # Call the function to list tools
    tools = await list_tools_from_mcp_server()
    print(tools)

# Run the main function
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())