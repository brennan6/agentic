import openai
import re
import httpx
import os
import sys
from dotenv import load_dotenv

_ = load_dotenv()
from openai import OpenAI

# SECRETS:
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
region="us1"
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY")

# OpenAI client:
# client = OpenAI(api_key=OPENAI_API_KEY)
client = openai.OpenAI(api_key=LITELLM_API_KEY, base_url=f"https://litellm-api.{region}.salesloft.com") 

# Prompt, because less concerned about this:
prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

average_dog_weight:
e.g. average_dog_weight: Collie
returns average weight of a dog when given the breed

Example session:

Question: How much does a Bulldog weigh?
Thought: I should look the dogs weight using average_dog_weight
Action: average_dog_weight: Bulldog
PAUSE

You will be called again with this:

Observation: A Bulldog weights 51 lbs

You then output:

Answer: A bulldog weights 51 lbs
""".strip()



class Agent():

    def __init__(self, prompt="", model="gemini-1.5-flash-002"):
        self.prompt = prompt
        self.model = model
        self.messages = []

        if self.prompt:
            self.messages.append({"role": "system", "content": self.prompt})
    
    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        response = self.execute(message)
        self.messages.append({"role": "assistant", "content": response.choices[0].message.content})

    def execute(self, message):
        response = client.chat.completions.create(
                                model=self.model,
                                temperature=0,
                                messages=self.messages
                            )
        return response



#tests:
# Test 1:
simple_agent = Agent(prompt)
simple_agent("How much does a Golden Retriever weigh?")
print(simple_agent.messages)

# Test 2:


