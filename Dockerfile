# Slim Python base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY chatbot.py .

# Environment
ENV PYTHONUNBUFFERED=1

# Railway will inject PORT
EXPOSE $PORT

# Start app
CMD sh -c "uvicorn chatbot:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --log-level info"
