from langchain_openai import ChatOpenAI
from contextlib import asynccontextmanager
from langchain_mcp_adapters.client import MultiServerMCPClient
from agent import BettingAgent
from langgraph.prebuilt import create_react_agent
import asyncio
import os
from uuid import uuid4
from langchain_core.messages import HumanMessage
import logging

from dotenv import load_dotenv

# Load environment variables:
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if os.getenv('OPENAI_API_KEY'):
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini")
else:
    print('Export OPENAI_API_KEY to initialize OpenAI LLM.')
    exit(1)

@asynccontextmanager
async def main():
    logger.info("Testing 1, 2, 3")
    client = MultiServerMCPClient({
        "mcp_server": {
            "url": os.getenv("REMOTE_MCP_URL", "http://localhost:8000/sse"),
            "transport": "sse"
            }
        })
    tools = await client.get_tools()
    # Filter tools to include only the necessary ones for itinerary planning
    print(tools)
    tools = [tool for tool in tools if tool.name in ["search_tool"]]

    logger.info("Loaded MCP tools:" + ", ".join(tool.name for tool in tools))

    # agent = create_react_agent(
    #         llm, 
    #         tools=tools,
    #         prompt="You are a helpful assistant. After answering the question please provide me with a list of the tools used."
    #     )
    agent = BettingAgent(llm, tools=tools)
    
    yield agent

async def invoke_agent(query):
    async with main() as agent:
        # agent_response = await agent.execute(query)
        session_id = str(uuid4())
        initial_state = {"session_id": session_id,
                         "messages": [HumanMessage(content=query)],
                         "query": query}
        agent_response = await agent.graph.ainvoke(initial_state)
        print("==== Final Answer ====")
        print(agent_response['messages'])


if __name__ == "__main__":
    
    query = "Who won game 5 of the NBA Finals this year. The year is 2025"
    asyncio.run(invoke_agent(query=query))