# Backend Dockerfile for Reflecto (FastAPI + Uvicorn)
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code (UPDATED ARCHITECTURE)
COPY api ./api
COPY app ./app
COPY reflecto ./reflecto
COPY domain ./domain
COPY application ./application
COPY infrastructure ./infrastructure
COPY extensions ./extensions
COPY contracts ./contracts

# Misc project files
COPY seed_patterns.py .
COPY setup.py .
COPY LICENSE .
COPY README.md .

# Expose backend port
EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
