FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
# Avoiding massive torch downloads if not needed, using cpu-only wheel:
RUN pip install torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
