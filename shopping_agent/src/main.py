import os
import json
from openai import OpenAI

from datetime import date
from agent import ShoppingAgent
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from tools import notify
from build_response_class import build_response_class

def main(request):
    """
    TO DO: CLEAN 
    """
    region="us1"
    LITELLM_API_KEY = os.getenv("LITELLM_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # OpenAI:
    research_model = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini")
    response_model = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini")

    # LiteLLM:
    # research_model = ChatOpenAI(api_key=LITELLM_API_KEY, base_url=f"https://litellm-api.{region}.salesloft.com",
    #                             model="gemini-pro")  # requires more advanced model
    # response_model = ChatOpenAI(api_key=LITELLM_API_KEY, base_url=f"https://litellm-api.{region}.salesloft.com",
    #                             model="gemini-1.5-flash-002")

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

    with open("../configs/prompts.json", "r") as file:
        response_format = json.load(file)

    response_class = build_response_class(response_format)

    shopping_agent = ShoppingAgent(research_model=research_model, response_model=response_model,
                                   price=request["limit"], tools=tools, ResponseClass=response_class)
    output = shopping_agent._execute(user_prompt)

    return output


if __name__ == "__main__":
    request = {"item": "Atomic Bent 110 Skis 2024/2025",
               "limit": 600,
               "condition": "new",
               "phone_number": "867-75309",
               "size": 180,
               "profile": "adult"} 

    region="us1"
    LITELLM_API_KEY = os.getenv("LITELLM_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # OpenAI:
    research_model = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini")
    response_model = ChatOpenAI(api_key=OPENAI_API_KEY, model="gpt-4o")

    # LiteLLM:
    # research_model = ChatOpenAI(api_key=LITELLM_API_KEY, base_url=f"https://litellm-api.{region}.salesloft.com",
    #                             model="gemini-pro")  # requires more advanced model
    # response_model = ChatOpenAI(api_key=LITELLM_API_KEY, base_url=f"https://litellm-api.{region}.salesloft.com",
    #                             model="gemini-1.5-flash-002")

    tools = [TavilySearchResults(max_results=4), notify]
    user_prompt = (
            f"Today's date is {date.today()}. "
            f"Using the search function that is provided, research the price of {request['item']} given its {request['condition']}. "
            f"Your goal is to determine how this price compares to {request['limit']}, which is the maximum price the user would buy this item for. "
            f"If the researched price is less than user's maximum price it is your job to notify the user of this using the notify function by passing in {request['phone_number']}. "
            "Use the provided date to make sure your information is as up to date as possible. "
            f"""
            # REQUIREMENTS:
            - The name of the product researched.
            - The lowest price observed from research for this product given its {request['condition']}.
            - The condition of the product.
            # FINAL OUTPUT:
            - Structure the final output payload as a JSON object containing the item, lowest price, and condition.
            - Do not explain any of these fields."""
        )

    with open("./configs/prompts.json", "r") as file:
        response_format = json.load(file)

    response_class = build_response_class(response_format)

    shopping_agent = ShoppingAgent(research_model=research_model, response_model=response_model,
                                   tools=tools, ResponseClass=response_class)
    output = shopping_agent._execute(user_prompt)

    print("\n\nOutput:")
    print(output)

    