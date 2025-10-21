#!/bin/bash

# Start script for NetWiz Docker-in-Docker container
# Usage: ./dind/start.sh [port] [data-dir] [env-file] (or call from any directory)

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of script directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root directory
cd "$PROJECT_ROOT"

# Default port
PORT=${1:-8080}
# Optional data directory for MongoDB persistence
DATA_DIR=${2:-}
# Optional .env file for backend configuration
ENV_FILE=${3:-}

echo "🚀 Starting NetWiz with Docker-in-Docker"
echo "========================================="
echo "Using port: $PORT"
if [ -n "$DATA_DIR" ]; then
    echo "Using data directory: $DATA_DIR"
else
    echo "Using ephemeral data (no persistence)"
fi
if [ -n "$ENV_FILE" ]; then
    echo "Using .env file: $ENV_FILE"
else
    echo "Using default backend configuration"
fi

# Build docker run command
DOCKER_CMD="docker run --rm --privileged -p $PORT:80"

# Add data volume mount if specified
if [ -n "$DATA_DIR" ]; then
    DOCKER_CMD="$DOCKER_CMD -v $DATA_DIR:/data"
fi

# Add .env file mount if specified
if [ -n "$ENV_FILE" ]; then
    DOCKER_CMD="$DOCKER_CMD -v $ENV_FILE:/app/backend.env"
fi

# Run the Docker-in-Docker container
$DOCKER_CMD netwiz-dind

echo "✅ NetWiz is running at http://localhost:$PORT"
echo "   - Frontend: http://localhost:$PORT/"
echo "   - Backend API: http://localhost:$PORT/api/"
echo "   - Backend Docs: http://localhost:$PORT/docs"
