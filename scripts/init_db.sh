#!/bin/bash
# Database initialization script for production
# Ensures data directory exists and initializes database

set -e

# Create data directory if it doesn't exist
mkdir -p /app/data

# Set proper permissions
chmod 755 /app/data

# Initialize database using Python
echo "Initializing database..."
cd /app
uv run python -c "from backend.database.db import init_db; init_db()"

echo "Database initialized successfully"

