
# from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool

@tool
def notify(phone_number: str, price: int) -> str:
    """Notify the user."""
    print(f"Sent text to {phone_number}.")
    return f"Sent text to {phone_number}."