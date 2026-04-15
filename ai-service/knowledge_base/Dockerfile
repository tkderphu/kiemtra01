FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .

# Install dependencies and C++ compiler for chromadb
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure data directory exists
RUN mkdir -p /data/chroma

# Build KB on start (with mock or real key depending on env)
RUN python embedder.py

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "1"]
