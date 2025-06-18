
from uuid import uuid4
import operator
import logging
from typing import TypedDict, Annotated, List
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, ToolMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

load_dotenv()

class State(TypedDict):
    """
    Represents the state of our agent.

    Attributes:
        messages: The history of messages in the conversation.
    """
    session_id: str
    messages: Annotated[List[dict], operator.add]
    query: str

class BettingAgent:
    """
    Encapsulates the logic for our LangGraph betting agent.
    """
    def __init__(self, model, tools):
        # self.tools = {t.name: t for t in tools}
        self.tools = tools
        self.model = model.bind_tools(tools)
        self.graph = self._build_graph()
        self.attempts = 0

    def _build_graph(self):
        """Builds the state graph for the agent's workflow."""
        workflow = StateGraph(State)

        # Define the two nodes in our graph: the agent and the tool executor
        workflow.add_node("agent", self.call_model)
        workflow.add_node("action", self.call_tool)

        # The entry point is the agent node
        workflow.set_entry_point("agent")

        # Define the conditional logic for routing
        workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "continue": "action",
                "end": END,
            },
        )
        
        # After an action, always go back to the agent to process the results
        workflow.add_edge("action", "agent")

        # Compile the graph into a runnable application
        return workflow.compile()

    def call_model(self, state: State):
        """
        The primary "thinking" node. It calls the LLM to decide the next step.
        """
        messages = state["messages"]
        logging.info("AGENT: Thinking...")
        self.attempts += 1

        prompt = f"""
                    You are a highly analytical betting research agent.
                    Your goal is to provide a clear recommendation on whether to bet on a given matchup.

                    Analyze all the gathered information (research and odds) to provide a final answer.

                    Your final answer must start with 'DECISION:' and be either 'Place the bet.' or 'Do not bet.', followed by your reasoning.
                    Do not ask clarifying questions. Follow the process and provide a final decision.

                    Here is a snapshot of your conversation history: {messages}

            """
        response = self.model.invoke(prompt)
        # The response from the LLM is added to the state
        return {"messages": [response]}

    def call_tool(self, state: State):
        """
        This node executes the tool chosen by the agent.
        """
        last_message = state["messages"][-1]
        
        # We know this is an AIMessage with tool_calls because of our routing logic
        tool_call = last_message.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        logging.info(f"AGENT: Executing tool '{tool_name}' with args {tool_args}")
        
        # Find the correct tool function and execute it
        tool_function = next(t for t in self.tools if t.__name__ == tool_name)
        response = tool_function(**tool_args)
        
        # We return the tool's response as a ToolMessage
        return {"messages": [ToolMessage(content=str(response), tool_call_id=tool_call["id"])]}

    def should_continue(self, state: State):
        """
        Conditional routing logic. Decides whether to continue the loop or end.
        """
        last_message = state["messages"][-1]
        # If the LLM didn't call a tool, the conversation is over.
        if not last_message.tool_calls or self.attempts > 3:
            logging.info("AGENT: Decision reached. Ending workflow.")
            return "end"
        # Otherwise, continue to the action node to execute the tool.
        return "continue"
    
    def execute(self, user_query: str):
        """
        Runs the agent graph with the user's prompt and request data.

        Args:
            user_prompt (str): The initial prompt detailing the user's goal.
            request (dict): The dictionary of user-provided data.

        Returns:
            dict: The final output state from the graph execution.
        """
        session_id = str(uuid4())
        initial_state = {"session_id": session_id,
                         "messages": [HumanMessage(content=user_query)],
                         "query": user_query}
        return self.graph.invoke(initial_state)