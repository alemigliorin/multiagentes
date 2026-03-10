import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.tavily import TavilyTools

load_dotenv()

def test_search():
    print("Testing search with gpt-5-nano (expecting failure if ID is invalid)...")
    try:
        agent = Agent(
            model=OpenAIChat(id="gpt-4o-mini"),
            tools=[TavilyTools()],
        )
        response = agent.run("Qual a temperatura em São Paulo hoje?")
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Failed as expected or unexpected: {e}")

if __name__ == "__main__":
    test_search()
