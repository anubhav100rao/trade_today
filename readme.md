Make sure post 8000 is free

-
pip install -r requirements.txt

lsof -ti:8000 | xargs kill -9


run fastapi server

uvicorn api:app --reload --port 8000


curl http://localhost:8000/health

curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "Should I buy RELIANCE.NS?", "api_key": ""}'


-
Create .env file
GEMINI_API_KEY=your_gemini_api_key

--
