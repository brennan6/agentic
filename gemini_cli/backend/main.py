import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

# --- 1. Configuration and Initialization ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file. Please add it to the backend/.env file.")
genai.configure(api_key=gemini_api_key)

# --- 2. Tool Definition ---
def get_daily_betting_picks() -> str:
    """
    Fetches the top sports betting picks for the day.
    In a real application, this would call a sports data API.
    """
    logger.info("Tool Call: get_daily_betting_picks()")
    # Mock data for demonstration
    picks = [
        "Golden State Warriors -5.5 vs. Los Angeles Lakers",
        "Manchester United to win vs. Chelsea",
        "New York Yankees vs. Boston Red Sox - Over/Under 8.5 runs",
    ]
    return "Today's top betting picks are: " + ", ".join(picks)

# --- 3. Agent Definition ---
betting_agent = LlmAgent(
    model="gemini-1.5-flash",
    name="betting_agent",
    description="An agent that provides sports betting picks.",
    instruction="""You are a sports betting analyst. When the user asks for picks,
    use the `get_daily_betting_picks` tool to fetch the best bets for the day
    and present them to the user in a clear and concise bulleted list.""",
    tools=[get_daily_betting_picks],
)

# --- 4. ADK Runner and Session Setup ---
session_service = InMemorySessionService()
runner = Runner(
    agent=betting_agent,
    app_name="betting_app",
    session_service=session_service,
)

# --- 5. FastAPI Application ---
app = FastAPI()

# Configure CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/agent-picks")
async def get_agent_picks():
    """
    This endpoint invokes the ADK agent to get betting picks.
    """
    user_id = "default_user"
    session_id = "default_session"

    # Create a session if it doesn't exist
    try:
        session_service.get_session(app_name=runner.app_name, user_id=user_id, session_id=session_id)
    except Exception:
        session_service.create_session(app_name=runner.app_name, user_id=user_id, session_id=session_id)

    # Create the user message for the agent
    user_message = Content(role='user', parts=[Part.from_text("What are the best bets for today?")])

    final_response = "Sorry, I couldn't get the picks for today."
    try:
        # Run the agent asynchronously
        event_stream = runner.run_async(user_id=user_id, session_id=session_id, new_message=user_message)

        # Process the event stream to find the final response
        async for event in event_stream:
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
                logger.info(f"Agent's final response: {final_response}")
                break # Exit after getting the first final response

    except Exception as e:
        logger.error(f"An error occurred while running the agent: {e}")
        return {"error": "Failed to get picks from the agent."}

    # The agent's response might be a string that needs to be parsed.
    # For this example, we'll assume the agent returns a string with bullet points.
    # A more robust solution would be to have the agent return JSON.
    picks_list = [pick.strip() for pick in final_response.replace("Today's top betting picks are:", "").split(',')]

    return {"picks": picks_list}
