import os
import sys
from langchain_openai import ChatOpenAI
from langchain_core.messages import  HumanMessage
from dotenv import load_dotenv

# Load environment variables:
load_dotenv()

sys.path.extend([os.getenv('MCP_PATH')])
from agent import BettingAgent
from tools import search_tool

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if __name__ == "__main__":
    # Define the LLM model we'll use
    llm = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini")
    tools = [search_tool]

    # Create an instance of our agent
    betting_agent = BettingAgent(model=llm, tools=tools)

    # The user's question
    user_query = "What do you think about the Pacers vs. Thunder tomorrow night, 2025 NBA finals game 6?"

    output = betting_agent.execute(user_query)
    print(output['messages'][-1])