import asyncio
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient
from dotenv import load_dotenv
import os


# load api
load_dotenv()
groq_api = os.environ.get("GROQ_API_KEY")


async def main():
    client = MCPClient(config=
    {
        "mcpServers": {
            "filesystem": {
                "command": "python",
                "args": [
                    "/home/mahmoud/Documents/Work/Freelance/Upwork/Edu_Advisor_Agent/Servers/filesystem_server_v1.2.py",
                    "/home/mahmoud/Documents/Work/Freelance/Upwork/Edu_Advisor_Agent/resourses"],
            }
        }
    }
    )

    # Create LLM
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key= groq_api)

    # Create agent with tools
    agent = MCPAgent(llm=llm, client=client)

    print('am here :(')

    # Run the query
    result = await agent.run("List all server resources.")
    print(result)
    print('am here :(')



if __name__ == "__main__":
    asyncio.run(main())