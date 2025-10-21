#!/bin/bash

# Build and test script for NetWiz Docker containers
# This script builds containers with a temporary tag, tests them, and retags if tests pass
# Usage: ./dind/build-and-test.sh [final-tag] [port] (or call from any directory)

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of script directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root directory
cd "$PROJECT_ROOT"

# Default final tag or use provided tag
FINAL_TAG=${1:-latest}
PORT=${2:-8080}
TEMP_TAG="temp-$(date +%s)-$$"  # Unique temporary tag with timestamp and PID

echo "🧪 Building and Testing NetWiz Docker Containers"
echo "================================================"
echo "Final tag: $FINAL_TAG"
echo "Port: $PORT"
echo "Temporary tag: $TEMP_TAG"

# Function to cleanup temporary tags
cleanup() {
    echo "🧹 Cleaning up temporary tags..."
    docker rmi netwiz-backend:$TEMP_TAG 2>/dev/null || true
    docker rmi netwiz-frontend:$TEMP_TAG 2>/dev/null || true
    docker rmi netwiz-nginx:$TEMP_TAG 2>/dev/null || true
    docker rmi netwiz:$TEMP_TAG 2>/dev/null || true
}
trap cleanup EXIT

# Step 1: Build with temporary tag
echo "📦 Step 1: Building containers with temporary tag..."
./dind/build.sh $TEMP_TAG

if [ $? -ne 0 ]; then
    echo "❌ Build failed with temporary tag"
    exit 1
fi

echo "✅ Build completed successfully with temporary tag: $TEMP_TAG"

# Step 2: Test the temporary tag
echo "🧪 Step 2: Testing containers with temporary tag..."
./dind/test.sh netwiz:$TEMP_TAG $PORT

if [ $? -ne 0 ]; then
    echo "❌ Tests failed with temporary tag: $TEMP_TAG"
    echo "Containers will not be retagged with final tag: $FINAL_TAG"
    exit 1
fi

echo "✅ All tests passed with temporary tag: $TEMP_TAG"

# Step 3: Retag with final tag
echo "🏷️ Step 3: Retagging containers with final tag: $FINAL_TAG"
docker tag netwiz-backend:$TEMP_TAG netwiz-backend:$FINAL_TAG
docker tag netwiz-frontend:$TEMP_TAG netwiz-frontend:$FINAL_TAG
docker tag netwiz-nginx:$TEMP_TAG netwiz-nginx:$FINAL_TAG
docker tag netwiz:$TEMP_TAG netwiz:$FINAL_TAG

echo "✅ All containers successfully retagged with final tag: $FINAL_TAG"
echo ""
echo "Built and tested containers:"
echo "  - netwiz-backend:$FINAL_TAG"
echo "  - netwiz-frontend:$FINAL_TAG"
echo "  - netwiz-nginx:$FINAL_TAG"
echo "  - netwiz:$FINAL_TAG"
echo ""
echo "To start NetWiz:"
echo "  docker run --rm -it -p 8080:80 netwiz:$FINAL_TAG"
echo ""
echo "With data persistence:"
echo "  docker run --rm -it -p 8080:80 -v ./data:/data netwiz:$FINAL_TAG"
