#!/bin/bash

# Integration tests for NetWiz container
# Usage: ./dind/test.sh <image-name> [port] [timeout] (or call from any directory)

set -e
# Keep original fds
exec 3>&1 4>&2

# Prefix & line-buffer script output so it doesn't get stuck behind pipes
exec 1> >(sed -u 's/^/[script] /' >&3) \
     2> >(sed -u 's/^/[script-err] /' >&4)

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the project root directory (parent of script directory)
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Change to project root directory
cd "$PROJECT_ROOT"

IMAGE_NAME=${1:-netwiz}
PORT=${2:-8080}
TEST_TIMEOUT=${3:-300}  # 5 minutes timeout

echo "🧪 Testing NetWiz Container"
echo "============================"
echo "Image: $IMAGE_NAME"
echo "Port: $PORT"
echo "Timeout: ${TEST_TIMEOUT}s"


# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    if [ -n "$LOG_PID" ]; then
        kill -9 $LOG_PID 2>/dev/null || true
    fi
    if [ -n "$CONTAINER_ID" ]; then
        docker stop $CONTAINER_ID 2>/dev/null || true
        docker rm $CONTAINER_ID 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Test 1: Container can start
echo "📦 Test 1: Container startup"
CONTAINER_ID=$(docker run -d -p $PORT:80 --privileged $IMAGE_NAME)
echo "Container ID: $CONTAINER_ID"

# Wait for container to be ready with log streaming
echo "⏳ Waiting 30 seconds for container to fully start..."
echo "📋 Container logs (30 seconds):"
echo "----------------------------------------"

# Use a proper approach - run logs in background and kill after timeout
# Stream container logs for the whole run (do NOT stop it)
docker logs -f "$CONTAINER_ID" 2>&1 | sed -u 's/^/[container] /' >&3 &
LOGS_PID=$!
trap 'kill "$LOGS_PID" 2>/dev/null || true' EXIT

# now your echos will still show
echo "⏳ Waiting 20 seconds for container to fully start..."
sleep 10
echo "10 more seconds..."
sleep 10


echo "----------------------------------------"
echo "✅ Container startup complete"

# Test 2: Health endpoint
echo "🏥 Test 2: Health endpoint"
for i in $(seq 1 10); do
    echo "Health check attempt $i..."
    if curl -f --connect-timeout 10 --max-time 30 http://localhost:$PORT/health; then
        echo "✅ Health endpoint is responding"
        break
    else
        echo "❌ Health endpoint not responding, attempt $i failed"
        if [ $i -eq 10 ]; then
            cleanup
            echo ""
            echo "❌ Health endpoint failed after 10 attempts"
            exit 1
        fi
        sleep 5
    fi
done

# Test 3: Frontend is accessible
echo "🌐 Test 3: Frontend accessibility"
if curl -f --connect-timeout 10 --max-time 30 http://localhost:$PORT/; then
    echo "✅ Frontend is accessible"
else
    cleanup
    echo ""
    echo "❌ Frontend is not accessible"
    exit 1
fi

# Test 4: Backend API endpoints
echo "🔌 Test 4: Backend API endpoints"

# Test root API endpoint
if curl -f --connect-timeout 10 --max-time 30 http://localhost:$PORT/api/; then
    echo "✅ API root endpoint is responding"
else
    cleanup
    echo ""
    echo "❌ API root endpoint failed"
    exit 1
fi

# Test info endpoint
if curl -f --connect-timeout 10 --max-time 30 http://localhost:$PORT/info; then
    echo "✅ Info endpoint is responding"
else
    cleanup
    echo ""
    echo "❌ Info endpoint failed"
    exit 1
fi

# Test OpenAPI endpoint
if curl -f --connect-timeout 10 --max-time 30 http://localhost:$PORT/api/openapi.json; then
    echo "✅ OpenAPI endpoint is responding"
else
    cleanup
    echo ""
    echo "❌ OpenAPI endpoint failed"
    exit 1
fi

# Test 5: Static assets
echo "📁 Test 5: Static assets"
if curl -f --connect-timeout 10 --max-time 30 http://localhost:$PORT/logo-full.svg; then
    echo "✅ Static assets are accessible"
else
    cleanup
    echo ""
    echo "❌ Static assets are not accessible"
    exit 1
fi


echo ""
echo "✅ NetWiz container is working correctly"
echo "📊 Container is running on port $PORT"
echo "🔗 Access the application at: http://localhost:$PORT"
echo "📖 API documentation at: http://localhost:$PORT/docs"
cleanup
echo ""
echo "🎉 All integration tests passed!"
exit 0
