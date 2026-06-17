import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.1-8b-instant"


def get_llm(temperature: float = 0.0):
    """Returns a configured ChatGroq client. temperature=0 for deterministic
    tasks (classification), higher for generative writing tasks (report, remediation)."""
    return ChatGroq(model=MODEL_NAME, api_key=API_KEY, temperature=temperature)