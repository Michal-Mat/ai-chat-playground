#!/bin/bash
# Build script for the Hugging Chat application

set -e  # Exit on any error

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
IMAGE_NAME="hugging-chat"
TAG=${1:-latest}
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

echo "🐳 Building Docker image: ${FULL_IMAGE_NAME}"
echo "📁 Build context: ${PROJECT_ROOT}"
echo "🐳 Dockerfile: ${PROJECT_ROOT}/docker/Dockerfile"

# Build the Docker image from project root with dockerfile in docker/
docker build \
    --file "${PROJECT_ROOT}/docker/Dockerfile" \
    --tag "${FULL_IMAGE_NAME}" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --progress=plain \
    "${PROJECT_ROOT}"

echo "✅ Docker image built successfully: ${FULL_IMAGE_NAME}"

# Show image info
echo ""
echo "📊 Image information:"
docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo ""
echo "🚀 To run the application:"
echo "   docker run -p 8501:8501 --env-file ${PROJECT_ROOT}/.env ${FULL_IMAGE_NAME}"
echo ""
echo "🔧 To run with external services (MongoDB, Qdrant):"
echo "   docker compose -f ${PROJECT_ROOT}/docker/local.yml up -d  # Start services"
echo "   docker run -p 8501:8501 --env-file ${PROJECT_ROOT}/.env --network hugging_default ${FULL_IMAGE_NAME}"
