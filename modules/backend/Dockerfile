FROM python:3.11-slim

# Imposta variabili di ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Crea directory di lavoro
WORKDIR /app

# Copia e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione
COPY . .

# Crea utente non-root
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Esponi la porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ping || exit 1

# Comando di avvio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 