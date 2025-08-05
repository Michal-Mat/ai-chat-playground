#!/bin/bash
# Cleanup script to free up disk space before building

set -e

echo "🧹 Cleaning up disk space..."

# Clean Docker artifacts (skip if Docker is having issues)
echo "🐳 Cleaning Docker artifacts..."
if docker info > /dev/null 2>&1; then
    echo "Docker is running, cleaning..."
    docker system prune -f || true
    docker builder prune -f || true
else
    echo "Docker not available or having issues, skipping..."
fi

# Clean Python cache
echo "🐍 Cleaning Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Clean pip cache
echo "📦 Cleaning pip cache..."
pip cache purge || true

# Clean pytest cache
echo "🧪 Cleaning pytest cache..."
rm -rf .pytest_cache/ 2>/dev/null || true

# Clean ruff cache
echo "🔍 Cleaning ruff cache..."
rm -rf .ruff_cache/ 2>/dev/null || true

# Show disk usage
echo ""
echo "💾 Current disk usage:"
df -h / | tail -1

echo "✅ Cleanup complete!"
