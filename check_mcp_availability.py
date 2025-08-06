from dotenv import load_dotenv
from agents import Agent, Runner, trace
import os
import asyncio

# Try different import paths for MCP
try:
    # Option 1: Direct MCP imports
    from agents.mcp.server import MCPServerStdio, MCPServerStdioParams
    print("Using agents.mcp.server imports")
except ImportError:
    try:
        # Option 2: From mcp package directly
        from mcp.client.stdio import stdio_client, StdioServerParameters
        from mcp import StdioClientSession
        print("Using direct mcp imports")
        MCPServerStdio = None  # We'll handle this differently
    except ImportError:
        try:
            # Option 3: Check what's actually available
            import agents.mcp
            print("Available in agents.mcp:", dir(agents.mcp))
            # You can also check the __init__.py file to see what's exported
        except ImportError as e:
            print(f"MCP not available: {e}")

load_dotenv(override=True)

async def main():
    if MCPServerStdio is not None:
        # Using agents library MCP wrapper
        fetch_params = MCPServerStdioParams(command="uvx", args=["mcp-server-fetch"])
        async with MCPServerStdio(params=fetch_params, client_session_timeout_seconds=60) as server:
            fetch_server_tools = await server.list_tools()
        print("Fetch server tools:", fetch_server_tools)
    else:
        # Using direct MCP library
        from mcp.client.stdio import stdio_client
        from mcp import StdioClientSession
        
        server_params = StdioServerParameters(
            command="uvx",
            args=["mcp-server-fetch"]
        )
        
        async with stdio_client(server_params) as streams:
            read, write = streams
            async with StdioClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # List available tools
                tools_result = await session.list_tools()
                print("Fetch server tools:", tools_result.tools)

if __name__ == "__main__":
    asyncio.run(main())