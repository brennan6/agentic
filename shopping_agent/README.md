### AI Price Tracker & Notification Agent
An autonomous agent built with Python and LangGraph to monitor product prices online and send alerts for good deals.

### Overview
This project implements an AI-powered "shopping agent" that can be tasked with researching a specific product. It uses large language models (LLMs) from OpenAI to understand user requests, the Tavily search API to perform real-time web research, and a conditional logic graph built with LangGraph to execute its tasks.

The agent's primarsy goal is to find the current price of an item, compare it against a user-defined limit, and automatically trigger a notification if the item is available for purchase below that price.

### Key Technologies
Python 3.9+
LangChain & LangGraph: For orchestrating the agent's logic and state management.
OpenAI: For the core reasoning and response generation models (e.g., gpt-4o-mini).
Tavily: For efficient and accurate web search results.

### Features
Automated Web Research: Uses the Tavily search tool to find current product information and pricing.
Dynamic Price Comparison: Intelligently compares the lowest found price against a user-provided budget limit.
Conditional Notifications: Only triggers a notification if a price is found that is lower than the user's limit.
Structured JSON Output: Returns a clean, predictable JSON object with the final research results.
Stateful Execution: Uses a LangGraph StateGraph to manage the flow of information and decisions through a series of defined steps (nodes).
How It Works
The agent operates as a state machine, moving through a graph of nodes. Each node performs a specific action, and the graph's edges determine the next step.

### How It Works

The agent operates as a state machine, moving through a graph of nodes. The [LangGraph](https://python.langchain.com/v0.2/docs/langgraph/) framework manages the state and transitions based on the following logic:

```mermaid
graph TD
    A["[Start: User Request]"] --> B["1. LLM (Plan)"];
    B --> C["2. Search (Tavily)"];
    C --> D["3. LLM (Process Results)"];
    D --> E{"4. Deal Found?"};
    E -->|Yes| F["5. Notify User"];
    E -->|No| G["[END]"];
    F --> H["6. Generate Final Output"];
    H --> I["[END]"];

### Getting Started
Follow these steps to set up and run the project locally.

### Prerequisites
Python 3.9 or later
An OpenAI API Key
A Tavily API Key
Installation
Clone the repository:

### Bash

git clone https://your-repo-url/agentic.git
cd shopping_agent
Create and activate a virtual environment:


# For macOS / Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
Install the required dependencies:
Create a requirements.txt file with the following content:

Plaintext

langchain
langgraph
langchain-openai
langchain-community
tavily-python
python-dotenv
Then, install the packages:


pip install -r requirements.txt
Configuration
Create a file named .env in the root of your project directory.

Add your API keys to this file. This keeps your secret keys out of the source code.

.env file:

OPENAI_API_KEY="your_openai_api_key_here"
TAVILY_API_KEY="your_tavily_api_key_here"

# Add any other keys needed for your notification service (e.g., Twilio)
Usage
You can run the agent by calling the main function from a script.

Ensure your main function and the ShoppingAgent class are in your project files (e.g., agent.py).

Create a run.py file to execute the agent:

run.py:

Python

import os
from dotenv import load_dotenv
from agent import main # Assuming your main function is in agent.py

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Define the user's request for the agent
    user_request = {
        "item": "Atomic Bent 110 Skis 2025",
        "condition": "new",
        "limit": 500,
        "phone_number": "+15551234567", # Example phone number
        "size": "180cm",
        "profile": "Freeride"
    }

    print("🚀 Starting the AI Shopping Agent...")
    print(f"   Searching for: {user_request['item']}")
    print(f"   Price limit: ${user_request['limit']}")

    # Execute the agent
    result = main(user_request)

    print("\n✅ Agent finished execution.")
    print("Final Output:")
    print(result)

Run the script from your terminal:

python run.py
Future Improvements
[ ] Add support for more notification channels (Email, Slack, Discord).
[ ] Integrate more search tools for wider product coverage.
[ ] Build a simple web interface (using Flask or FastAPI) to interact with the agent.
[ ] Implement a database to track price history over time.