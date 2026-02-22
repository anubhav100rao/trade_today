import os
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

try:
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    res = embeddings.embed_query("hello")
    print("Success: text-embedding-004")
except Exception as e:
    print(f"Error 004: {e}")

try:
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    res = embeddings.embed_query("hello")
    print("Success: embedding-001")
except Exception as e:
    print(f"Error 001: {e}")
