# Multi-stage Docker build for production deployment
FROM python:3.12-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# uv sync creates a virtual environment and installs dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY main.py ./
COPY api_client.py ./
COPY models/ ./models/
COPY data/ ./data/
COPY scripts/ ./scripts/

# Make scripts executable
RUN chmod +x /app/scripts/*.sh

# Create data directory for database persistence
RUN mkdir -p /app/data && chmod 755 /app/data

# Copy jobs.json to config dir (backup for volume mounts that shadow /app/data)
RUN mkdir -p /app/config && cp /app/data/jobs.json /app/config/jobs.json

# Expose ports
EXPOSE 8000 8501

# Set default command
CMD ["/app/scripts/start.sh"]

