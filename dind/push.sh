#!/bin/bash

# Push script for NetWiz Docker containers
# This script pushes all Docker containers to GHCR
# Usage: ./dind/push.sh [tag] [registry] (or call from any directory)

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of script directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root directory
cd "$PROJECT_ROOT"

# Default values
TAG=${1:-latest}
REGISTRY=${2:-ghcr.io}
USER=${3:-modularizer}

echo "🚀 Pushing NetWiz Docker Containers"
echo "==================================="
echo "Using tag: $TAG"
echo "Using registry: $REGISTRY"


# Push all containers
echo "📦 Pushing backend container..."
docker tag netwiz-backend:$TAG $REGISTRY/$USER/netwiz-backend:$TAG
docker push $REGISTRY/$USER/netwiz-backend:$TAG

echo "📦 Pushing frontend container..."
docker tag netwiz-frontend:$TAG $REGISTRY/$USER/netwiz-frontend:$TAG
docker push $REGISTRY/$USER/netwiz-frontend:$TAG

echo "📦 Pushing nginx container..."
docker tag netwiz-nginx:$TAG $REGISTRY/$USER/netwiz-nginx:$TAG
docker push $REGISTRY/$USER/netwiz-nginx:$TAG

echo "📦 Pushing netwiz container..."
docker tag netwiz:$TAG $REGISTRY/$USER/netwiz:$TAG
docker push $REGISTRY/$USER/netwiz:$TAG

echo "✅ All containers pushed successfully!"
echo ""
echo "Pushed containers:"
echo "  - $REGISTRY/$USER/netwiz-backend:$TAG"
echo "  - $REGISTRY/$USER/netwiz-frontend:$TAG"
echo "  - $REGISTRY/$USER/netwiz-nginx:$TAG"
echo "  - $REGISTRY/$USER/netwiz:$TAG"
echo ""
echo "To pull and run:"
echo "  docker pull $REGISTRY/$USER/netwiz:$TAG  && docker run --rm --privileged -p 8080:80 $REGISTRY/$USER/netwiz:$TAG"
