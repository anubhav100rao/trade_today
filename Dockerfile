FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if any are needed by yfinance, pandas, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose ports for both FastAPI and Streamlit
EXPOSE 8000 8501

# Default command (will run FastAPI by default if not overridden)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
