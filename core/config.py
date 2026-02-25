from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

# We get the API key from the environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_llm(temperature: float = 0.2):
    """Returns a configured Gemini LLM instance."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=GEMINI_API_KEY, 
        temperature=temperature
    )
