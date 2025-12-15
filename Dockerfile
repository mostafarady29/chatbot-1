# ============================================
# STAGE 1: Builder - Install dependencies
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install to a local directory
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================
# STAGE 2: Runtime - Minimal final image
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY chatbot.py .

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE $PORT

# Run app (model will download on first request)
CMD sh -c "uvicorn chatbot:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1 --log-level info"
