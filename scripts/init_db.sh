#!/bin/bash
# Database initialization script for production
# Ensures data directory exists and initializes database

set -e

# Create data directory if it doesn't exist
mkdir -p /app/data

# Set proper permissions
chmod 755 /app/data

# Copy jobs.json if it doesn't exist (volume mounts shadow the Docker COPY)
if [ ! -f /app/data/jobs.json ] && [ -f /app/config/jobs.json ]; then
    echo "Copying jobs.json to data directory..."
    cp /app/config/jobs.json /app/data/jobs.json
fi

# Initialize database using Python
echo "Initializing database..."
cd /app
uv run python -c "from backend.database.db import init_db; init_db()"

echo "Database initialized successfully"

