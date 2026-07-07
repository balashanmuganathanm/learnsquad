import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\mbala\\Claude"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])

            # Example: list directory
            result = await session.call_tool(
                "list_directory",
                arguments={"path": "C:\\Users\\mbala\\Claude"}
            )
            lines = result.content[0].text.strip().split("\n")

            files=[]
            for line in lines:
                if (line.startswith("[FILE]")):
                    files.append(line[7:])
            print(files)
            
            # result = await session.call_tool(
            #     "read_file",
            #     arguments={"path": "C:\\Users\\mbala\\Claude\\nature_poem.txt"}
            # )
            # print(result.content[0].text)

asyncio.run(main())