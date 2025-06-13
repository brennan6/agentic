import os
import json
from openai import OpenAI

from datetime import date
from agent import ShoppingAgent
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from tools import notify

def main(request):
    """Initializes and executes a shopping agent to find and compare an item's price.

    This function sets up and runs an AI shopping agent with OpenAI models
    and tools. The agent researches an item's price online, compares it
    against a user-defined limit, and notifies the user if the item is
    within budget.

    Args:
        request (dict): A dictionary containing the user's search criteria.
            Expected keys include:
            - 'item' (str): The name of the product to research.
            - 'condition' (str): The condition of the item (e.g., 'new').
            - 'limit' (float or int): The maximum price the user will pay.
            - 'phone_number' (str): The user's phone number for notifications.
            - 'size' (str): The specific size of the product.
            - 'profile' (str): The specific style or profile of the product.

    Returns:
        dict: A dictionary (intended for JSON output) containing the research
              results, including the item name, lowest price, condition, and source.
    """
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # OpenAI:
    research_model = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini")
    response_model = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini")

    tools = [TavilySearchResults(max_results=4), notify]
    user_prompt = (
            f"Today's date is {date.today()}. "
            f"Using the search tool that is provided, research the price of {request['item']} given its {request['condition']}. "
            f"Your goal is to determine how this price compares to the price {request['limit']}, which is the maximum price the user would buy this item for. "
            f"If the researched price is less than the price {request['limit']} it is your job to notify the user of this using the notify tool by passing in {request['phone_number']}. "
            f"Make sure that the product corresponds to both size - {request['size']} and profile - {request['profile']} of the user. "
            "Use the provided date to make sure your information is as up to date as possible. "
            f"""
            # REQUIREMENTS:
            - The name of the product researched.
            - The lowest price observed from research for this product given its {request['condition']}.
            - The condition of the product.
            - The source where the lowest price for {request['item']} can be found in {request['condition']}. This is the price you should compare with {request['limit']}.
            - DO NOT use the notify tool unless you are positive that you have identified a price that is less than the price {request['limit']}.
            - DO NOT use the notify tool more than once.
            # FINAL OUTPUT:
            - Structure the final output payload as a JSON object containing the item, lowest price, condition, and source.
            - Do not explain any of these fields."""
        )

    shopping_agent = ShoppingAgent(research_model=research_model, response_model=response_model,
                                   limit_price=request['limit'], tools=tools)
    output = shopping_agent._execute(user_prompt, request)

    return output

if __name__ == "__main__":
    request = {"item": "Atomic Bent 110 Skis 2024/2025",
               "limit": 600,
               "condition": "new",
               "phone_number": "867-75309",
               "size": 180,
               "profile": "adult"} 
    
    output = main(request)
    print("\n\nOutput:")
    print(output)

    