#!/bin/bash

# Build script for NetWiz Docker-in-Docker setup
# This script builds the Docker-in-Docker container and all sub-containers

set -e

echo "🐳 Building NetWiz Docker-in-Docker setup"
echo "=========================================="

# Build the sub-containers first
echo "📦 Building backend container..."
docker build -t netwiz-backend:latest -f backend/Dockerfile backend

echo "📦 Building frontend container..."
docker build -t netwiz-frontend:latest -f frontend/Dockerfile frontend

echo "📦 Building nginx container..."
docker build -t netwiz-nginx:latest -f nginx/Dockerfile nginx

# Build the Docker-in-Docker container
echo "📦 Building Docker-in-Docker container..."
docker build -f Dockerfile.dind -t netwiz .

if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker-in-Docker container"
    exit 1
fi

echo "✅ All containers built successfully"
echo ""
echo "To start NetWiz using docker command:"
echo  "  docker run --rm -p 8080:80 -v /mongodb_data:/data"
echo ""
echo "Or use this script:"
echo "  ./startsh [port] [data-dir]"
echo ""
echo "Examples:"
echo "  ./start.sh                    # Use port 8080, ephemeral data"
echo "  ./start.sh 9000               # Use port 9000, ephemeral data"
echo "  ./start.sh 9000 ./data        # Use port 9000, persistent data in ./data"
echo ""
echo "The application will be available at:"
echo "  - Frontend: http://localhost:8080/"
echo "  - Backend API: http://localhost:8080/api/"
echo "  - Backend Docs: http://localhost:8080/docs"
