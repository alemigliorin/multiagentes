import logging
import os
import time

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.tavily import TavilyTools
from agno.utils.log import logger
from dotenv import load_dotenv

# Enable debug logging for agno to see the tool calls
logger.setLevel(logging.DEBUG)
load_dotenv()


def test_performance():
    # Force use of a known good model for this test to avoid ID issues
    model = OpenAIChat(id="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

    agent = Agent(
        model=model,
        tools=[TavilyTools()],
        instructions=open("prompts/pesquisador.md", encoding="utf-8").read(),
    )

    query = "Resultados do Campeonato Brasileiro Série A em 05/03/2026"
    print(f"Buscando: {query}...")

    start_time = time.time()
    response = agent.run(query)
    duration = time.time() - start_time

    print(f"\nTime taken: {duration:.2f} seconds")
    print(f"Response:\n{response.content[:500]}...")


if __name__ == "__main__":
    test_performance()
