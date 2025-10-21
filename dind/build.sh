#!/bin/bash

# Build script for NetWiz Docker containers
# This script builds all Docker containers for NetWiz
# Usage: ./dind/build.sh [tag] (or call from any directory)

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of script directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root directory
cd "$PROJECT_ROOT"

# Default tag or use provided tag
TAG=${1:-latest}

echo "🐳 Building NetWiz Docker Containers"
echo "====================================="
echo "Using tag: $TAG"

# Build the sub-containers first
echo "📦 Building backend container..."
docker build -t netwiz-backend:$TAG -f backend/Dockerfile backend

echo "📦 Building frontend container..."
docker build -t netwiz-frontend:$TAG -f frontend/Dockerfile frontend

echo "📦 Building nginx container..."
docker build -t netwiz-nginx:$TAG -f nginx/Dockerfile nginx

# Save locally built images as tar files for DinD
echo "💾 Saving locally built images as tar files..."
docker save -o netwiz-backend.tar netwiz-backend:$TAG
docker save -o netwiz-frontend.tar netwiz-frontend:$TAG
docker save -o netwiz-nginx.tar netwiz-nginx:$TAG

# Pull and save MongoDB image
echo "📥 Pulling and saving MongoDB image..."
docker pull mongo:7.0
docker save -o mongo.tar mongo:7.0

# Build the base DinD container
echo "📦 Building base DinD container..."
docker build -f dind/Dockerfile -t netwiz:$TAG .



echo "✅ All containers built successfully"
echo ""
echo "Built containers:"
echo "  - netwiz-backend:$TAG"
echo "  - netwiz-frontend:$TAG"
echo "  - netwiz-nginx:$TAG"
echo "  - netwiz:$TAG"
echo ""
echo "To start NetWiz:"
echo "  docker run --rm --privileged -p 8080:80 netwiz:$TAG"
echo ""
echo "With data persistence:"
echo "  docker run --rm --privileged -p 8080:80 -v ./data:/data netwiz:$TAG"
echo ""
echo "With custom .env file:"
echo "  docker run --rm --privileged -p 8080:80 -v ./backend/.env:/app/backend.env netwiz:$TAG"
