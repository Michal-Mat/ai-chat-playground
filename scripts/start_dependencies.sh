#!/bin/bash

# Start dependencies (MongoDB and Qdrant) from project root
echo "Starting dependencies..."

# Check if docker-compose is available
if ! command -v docker compose &> /dev/null; then
    echo "Error: docker compose is not installed or not available in PATH"
    exit 1
fi

# Navigate to the docker directory and start dependencies
cd docker && docker compose -f local.yml up -d

if [ $? -eq 0 ]; then
    echo "✅ Dependencies started successfully!"
    echo "📊 MongoDB available at: localhost:27017"
    echo "🔍 Qdrant available at: localhost:6333"
else
    echo "❌ Failed to start dependencies"
    exit 1
fi
