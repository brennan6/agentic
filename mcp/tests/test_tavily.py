import os
from tavily import TavilyClient
from dotenv import load_dotenv

# Load environment variables:
load_dotenv()

TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')

if __name__ == "__main__":
    # Step 1. Instantiating your TavilyClient
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

    # Step 2. Executing a Q&A search query
    answer = tavily_client.qna_search(query="Who won game 5 of the NBA Finals this year.")

    # Step 3. That's it! Your question has been answered!
    print(answer)