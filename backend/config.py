import os
from dotenv import load_dotenv

# Load .env from project root (one level up from backend/)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
HF_TOKEN: str = os.environ.get("HF_TOKEN", "")

GROQ_MODEL = "llama-3.1-8b-instant"

DATABASE_URL = "sqlite:///./health_assistant.db"
