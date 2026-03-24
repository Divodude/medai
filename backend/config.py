import os
from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")

GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

DATABASE_URL = "sqlite:///./health_assistant.db"
