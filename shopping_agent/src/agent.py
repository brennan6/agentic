import os
import json
from dotenv import load_dotenv
from typing import Any, List, Type
from pydantic import BaseModel, Field

# Load environment variables:
load_dotenv()

# Langgraph utils:
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

# Langchain utils:
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

class ShoppingAgent:
    """
    An agent meant to capture prices on products from specific sites and notify of any opportunities
    to purchase below initial bidding price.

    Attributes: Those that are not present on init.
        graph - StateGraph - The graph structure via Langgraph.
    """

    def __init__(self, research_model, response_model,
                 price, tools, ResponseClass: Type[BaseModel]):
        """
        Initialiazes the shopping Agent.
        -----
        Params:
            reserch_model - 
            response_model - 
            price - 
            tools - 
            ResponseClass - Type[BaseModel] - 
        -----
        Returns:
        """
        self.research_model = research_model
        self.response_model = response_model.with_structured_output(ResponseClass)

        self.graph = self._build_graph(tools)

        self.price = price

    def _build_graph(self, tools) -> StateGraph:
        """
        Builds the Langgraph based on the desired workflow.
        -----
        Params:
            tools - 
        """
        graph = StateGraph(MessagesState)

        # Define Nodes:
        graph.add_node("llm", self._call_llm)
        graph.add_node("shop", self._search)
        graph.add_node("process_shop", self._call_llm)
        graph.add_node("notify", self._notify)
        graph.add_node("output", self._output)

        # Define start:
        graph.set_entry_point("llm")

        # Define Edges:
        graph.add_edge("llm", "shop")
        graph.add_edge("shop", "process_shop")
        graph.add_conditional_edges(
            "process_shop",
            self._exists_deal,
            {True: "notify", False: END}
        )
        graph.add_edge("notify", "output")
        graph.add_edge("output", END)

        # Assign tools: 
        self.tools = {t.name: t for t in tools}
        self.research_model = self.research_model.bind_tools(tools)

        return graph.compile()

    def _call_llm(self, state: MessagesState) -> dict:
        """
        """
        return {"messages": [self.research_model.invoke(state["messages"])]}

    def _output(self, state: MessagesState) -> dict:
        """
        """
        final_response = self.response_model.invoke(state["messages"])
        print(final_response)
        # Format how we want to parse:
        output_d = {"item": final_response.item,
                    "price": final_response.price,
                    "condition": final_response.condition}

        return {"messages": [AIMessage(content=json.dumps(output_d))]}

    def _search(self, state: MessagesState) -> dict:
        """
        """
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            result = self.tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))

        return {'messages': results}

    def _notify(self, state: MessagesState) -> dict:
        """
        """
        tool = state['messages'][-1].tool_calls[0] if state['messages'][-1].tool_calls else None
        rejection_str = "Did not notify user."

        if tool is not None:
            print("Tool comparison price:", tool["args"]["price"])
            if tool["args"]["price"] < int(self.price):
                result = self.tools[tool['name']].invoke(tool['args'])
                return {'messages': [ToolMessage(tool_call_id=tool['id'], name=tool['name'], content=str(result))]}
            else:
                print("Made it here.")
                return {'messages': [ToolMessage(tool_call_id=tool['id'], name=tool['name'], content=rejection_str)]}
        else:
            return {'messages': [ToolMessage(tool_call_id=tool['id'], name=tool['name'], content=rejection_str)]}

    def _exists_deal(self, state: MessagesState) -> bool:
        """
        """
        tool = state['messages'][-1].tool_calls[0] if state['messages'][-1].tool_calls else None

        if tool is not None:
            return True
        else:
            return False

    def _execute(self, user_prompt: str):
        """
        """
        initial_state = {"messages": [HumanMessage(content=user_prompt)]}
        return self.graph.invoke(initial_state)