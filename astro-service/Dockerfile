# =====================================
# Singularity Astro-Service Dockerfile
# =====================================

FROM python:3.11-slim AS base

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory inside container
WORKDIR /app

# Install system dependencies required by Skyfield / sgp4
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libstdc++6 curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app source
COPY app ./app
COPY .env.example ./.env.example

# Expose the app port
EXPOSE 8000

# Default command: run with Uvicorn directly (simple, good for Railway/Render)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Alternative production command (comment above and uncomment below):
# CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "2"]
