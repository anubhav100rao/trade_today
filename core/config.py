from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

# We get the API key from the environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_llm(temperature: float = 0.2):
    """Returns a configured Gemini LLM instance."""
    model1 = "gemini-2.5-flash"
    model2 = "gemini-3-flash-preview"
    return ChatGoogleGenerativeAI(
        model=model1,
        google_api_key=GEMINI_API_KEY, 
        temperature=temperature
    )
