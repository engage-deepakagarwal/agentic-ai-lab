from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams, SseServerParams
from dotenv import load_dotenv
import os
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
import traceback
import asyncio

load_dotenv(override=True)

def ensure_sandbox():
    sandbox_path = os.path.abspath(os.path.join(os.getcwd(), "sandbox"))
    if not os.path.exists(sandbox_path):
        os.makedirs(sandbox_path)
    return sandbox_path

async def get_playwright_params():
    # Connect to Playwright MCP server via SSE (try /sse endpoint)
    # Run this command "npx @playwright/mcp@latest --port 8931" in a separate terminal and keep it running
    playwright_params = SseServerParams(
        url="http://localhost:8931/sse"
    )
    return playwright_params

async def get_filesystem_params():
    sandbox_path = ensure_sandbox()
    # Run this "npm install @modelcontextprotocol/server-filesystem diff"
    # Then run "npm i @modelcontextprotocol/server-filesystem" in a separate terminal and keep it running
    files_params = StdioServerParams(
        command="node",
        args=["./node_modules/@modelcontextprotocol/server-filesystem/dist/index.js", sandbox_path],
    )
    return files_params

async def main():
    instructions = """
        You browse the internet to accomplish your instructions.
        You are highly capable at browsing the internet independently to accomplish your task, 
        including accepting all cookies and clicking 'not now' as
        appropriate to get to the content you need. If one website isn't fruitful, try another. 
        Be persistent until you have solved your assignment,
        trying different options and sites as needed.
    """

    print("Preparing to start filesystem MCP server...")
    # Start filesystem server as subprocess, connect to Playwright server via SSE
    async with McpWorkbench(await get_filesystem_params()) as mcp_server_files:
        print("Started filesystem MCP server.")
        print("Preparing to connect to Playwright MCP server via SSE...")
        async with McpWorkbench(await get_playwright_params()) as mcp_server_browser:
            print("Connected to Playwright MCP server.")
            model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
            agent = AssistantAgent(
                name="investigator", 
                system_message=instructions, 
                model_client=model_client,
                workbench=[mcp_server_files, mcp_server_browser])

            message = TextMessage(
                content="Find a great recipe for Banoffee Pie, then summarize it in markdown to banoffee.md",
                source="user"
            )

            print("Testing list_tools for each workbench...")
            try:
                print("Listing tools for filesystem MCP...")
                tools_fs = await mcp_server_files.list_tools()
                print(f"Filesystem MCP tools: {tools_fs}")
                print("Listing tools for Playwright MCP...")
                tools_pw = await mcp_server_browser.list_tools()
                print(f"Playwright MCP tools: {tools_pw}")
            except Exception as e:
                print(f"Error during list_tools: {e}")
                traceback.print_exc()
                return

            print("Sending message to agent...")
            try:
                # Add a timeout to the agent.on_messages call
                result = await asyncio.wait_for(
                    agent.on_messages([
                        TextMessage(
                            content="Find a great recipe for Banoffee Pie. Summarize it in markdown format. Then, use the write_file tool to save your markdown summary to the file 'sandbox/banoffee.md'. Be sure to call the write_file tool with the full path 'sandbox/banoffee.md' and your markdown summary as the content.",
                            source="user"
                        )
                    ], cancellation_token=CancellationToken()),
                    timeout=120
                )
                print("Agent response received:")
                print(result.chat_message)
                # Try to print the contents of the written file
                banoffee_path = os.path.join("sandbox", "banoffee.md")
                if os.path.exists(banoffee_path):
                    print("\nContents of sandbox/banoffee.md:\n")
                    with open(banoffee_path, "r", encoding="utf-8") as f:
                        print(f.read())
                else:
                    print("banoffee.md was not created in the sandbox directory.")
            except Exception as e:
                print(f"Error during agent message handling: {e}")
                traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())