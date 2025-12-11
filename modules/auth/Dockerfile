FROM python:3.11-slim

WORKDIR /app

# Dipendenze sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Codice applicazione
COPY app/ ./app/

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

