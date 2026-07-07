import asyncio
import os
import json
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
import dotenv
import httpx
import base64

dotenv.load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
SERVER_COMMAND = "npx"
SERVER_ARGS = ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\mbala\\Claude"]
MCP_SERVER_SSE_URL = "https://localhost:8000/sse"  # myMCPServer: weather + RAG

anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

def load_file_as_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")

pdf_data = load_file_as_base64("C:\\Users\\mbala\\EE.pdf")
pdf_data_msg = {
    "role": "user",
    "content": [
        {
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_data}
        },
        {"type": "text", "text": "Summarize this document."}
    ]
}

img_data = load_file_as_base64("C:\\Users\\mbala\\Claude\\DSC_0303.jpg")
img_data_msg = {
    "role": "user",
    "content": [
        {
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": img_data}
        },
        {"type": "text", "text": "What is in this image?"}
    ]
}

def custom_httpx_factory(headers=None, timeout=None, auth=None):
    return httpx.AsyncClient(verify=False, headers=headers, timeout=timeout, auth=auth)

GET_CITY_TOOL = {
    "name": "getCityName",
    "description": "Get the city name based on the zip code.",
    "input_schema": {
        "type": "object",
        "properties": {
            "zip": {"type": "string", "description": "The zip code"}
        },
        "required": ["zip"]
    }
}

def getCityName(zip: str) -> str:
    print(f"getCityName called with zip: {zip}")
    return json.dumps({"zip": zip, "city": "my City " + zip})


async def run_chat():
    fs_server_params = StdioServerParameters(command=SERVER_COMMAND, args=SERVER_ARGS)

    # Two sessions: filesystem (stdio) + myMCPServer (SSE)
    async with stdio_client(fs_server_params) as (fs_read, fs_write):
        async with ClientSession(fs_read, fs_write) as fs_session:
            await fs_session.initialize()

            async with sse_client(MCP_SERVER_SSE_URL, httpx_client_factory=custom_httpx_factory) as (mcp_read, mcp_write):
                async with ClientSession(mcp_read, mcp_write) as mcp_session:
                    await mcp_session.initialize()

                    # Filesystem tools
                    fs_mcp_tools = await fs_session.list_tools()
                    tools = [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "input_schema": tool.inputSchema
                        }
                        for tool in fs_mcp_tools.tools
                    ]

                    # myMCPServer tools (weather + RAG combined)
                    my_mcp_tools = await mcp_session.list_tools()
                    my_mcp_tool_names = set()
                    for tool in my_mcp_tools.tools:
                        tools.append({
                            "name": tool.name,
                            "description": tool.description,
                            "input_schema": tool.inputSchema
                        })
                        my_mcp_tool_names.add(tool.name)

                    # Local tool
                    tools.append(GET_CITY_TOOL)

                    print("Tools available:", [t['name'] for t in tools])
                    print("\nSpecial commands: 'img', 'pdf', 'exit'\n")

                    messages = [
                        {
                            "role": "user",
                            "content": "Can you check what files are in the Claude directory using the list tool?"
                        }
                    ]

                    system_prompt = """You are a helpful assistant with access to multiple tools:
- Filesystem tools: read/write/list files
- Weather tools: get alerts and forecasts
- RAG tools: index files into a vector database and search them for relevant context.
  When a user asks a question about company policy, severence agreement or product details that may be answered by indexed documents, call search_documents first.
  Always cite the source document in your answer.
- getCityName: look up a city by zip code"""

                    # Agentic loop
                    while True:
                        response = anthropic.messages.create(
                            model="claude-haiku-4-5",
                            max_tokens=1024,
                            system=system_prompt,
                            messages=messages,
                            tools=tools
                        )

                        if response.stop_reason == "end_turn":
                            for block in response.content:
                                if hasattr(block, "text"):
                                    print("Claude:", block.text)

                            messages.append({"role": "assistant", "content": response.content})

                            getInput = input("\nYou: ").strip()
                            if getInput == "exit":
                                break
                            elif getInput == "img":
                                messages.append(img_data_msg)
                            elif getInput == "pdf":
                                messages.append(pdf_data_msg)
                            else:
                                messages.append({"role": "user", "content": getInput})

                        if response.stop_reason == "tool_use":
                            messages.append({"role": "assistant", "content": response.content})

                            tool_results = []
                            for block in response.content:
                                if block.type == "tool_use":
                                    print(f"  [Tool: {block.name}({block.input})]")

                                    if block.name == "getCityName":
                                        # Local Python function
                                        result_text = getCityName(**block.input)

                                    elif block.name in my_mcp_tool_names:
                                        # myMCPServer — weather + RAG (SSE)
                                        result = await mcp_session.call_tool(block.name, arguments=block.input)
                                        result_text = result.content[0].text

                                    else:
                                        # Filesystem MCP (stdio)
                                        result = await fs_session.call_tool(block.name, arguments=block.input)
                                        result_text = result.content[0].text

                                    tool_results.append({
                                        "type": "tool_result",
                                        "tool_use_id": block.id,
                                        "content": result_text
                                    })

                            messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    asyncio.run(run_chat())