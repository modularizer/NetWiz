#!/bin/bash

# Default port
PORT=${1:-8080}
# Optional data directory for MongoDB persistence
DATA_DIR=${2:-}

echo "🚀 Starting NetWiz with Docker-in-Docker"
echo "========================================="
echo "Using port: $PORT"
if [ -n "$DATA_DIR" ]; then
    echo "Using data directory: $DATA_DIR"
else
    echo "Using ephemeral data (no persistence)"
fi

# Build docker run command
DOCKER_CMD="docker run --rm -p $PORT:80"

# Add data volume mount if specified
if [ -n "$DATA_DIR" ]; then
    DOCKER_CMD="$DOCKER_CMD -v $DATA_DIR:/data"
fi

# Run the Docker-in-Docker container
$DOCKER_CMD netwiz-dind

echo "✅ NetWiz is running at http://localhost:$PORT"
echo "   - Frontend: http://localhost:$PORT/"
echo "   - Backend API: http://localhost:$PORT/api/"
echo "   - Backend Docs: http://localhost:$PORT/docs"
