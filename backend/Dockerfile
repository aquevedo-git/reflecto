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

# Copy backend source code
COPY api ./api
COPY app ./app
COPY reflecto ./reflecto
COPY persistence ./persistence
COPY extensions ./extensions
COPY contracts ./contracts
COPY seed_patterns.py .
COPY setup.py .
COPY LICENSE .
COPY README.md .

# Expose backend port
EXPOSE 8000

# Set environment variables (add more as needed)
ENV PYTHONUNBUFFERED=1

# Start FastAPI app with Uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
