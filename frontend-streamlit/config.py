import os
from dotenv import load_dotenv

load_dotenv()

# Backend API Configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "http://localhost:8000")
AGENT_ID = os.getenv("AGENT_ID", "orquestrador")

# Endpoints
AGENT_RUN_ENDPOINT = f"{BACKEND_HOST}/agents/{AGENT_ID}/runs"
