from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# We get the API key from the environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_llm(temperature: float = 0.2):
    """Returns a configured Gemini LLM instance."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=GEMINI_API_KEY, 
        temperature=temperature
    )



def get_openai_llm(temperature: float = 0.2):
    """Returns a configured OpenAI LLM instance."""
    return ChatOpenAI(
        model="gpt-4o",
        openai_api_key=OPENAI_API_KEY,
        temperature=temperature
    )