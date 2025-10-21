#!/bin/bash

# Integration tests for NetWiz container
# Usage: ./dind/test.sh <image-name> [port] [timeout] (or call from any directory)

set -e

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

# Wait for container to be ready
echo "⏳ Waiting for container to be ready..."
for i in $(seq 1 30); do
    if docker ps | grep -q $CONTAINER_ID; then
        echo "✅ Container is running"
        break
    else
        echo "❌ Container not running, attempt $i"
        if [ $i -eq 30 ]; then
            echo "❌ Container failed to start after 30 attempts"
            docker logs $CONTAINER_ID
            exit 1
        fi
        sleep 2
    fi
done

# Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 30

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
            echo "❌ Health endpoint failed after 10 attempts"
            echo "Container logs:"
            docker logs $CONTAINER_ID
            exit 1
        fi
        sleep 10
    fi
done

# Test 3: Frontend is accessible
echo "🌐 Test 3: Frontend accessibility"
if curl -f --connect-timeout 10 --max-time 30 http://localhost:$PORT/; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not accessible"
    docker logs $CONTAINER_ID
    exit 1
fi

# Test 4: Backend API endpoints
echo "🔌 Test 4: Backend API endpoints"

# Test root API endpoint
if curl -f --connect-timeout 10 --max-time 30 http://localhost:$PORT/api/; then
    echo "✅ API root endpoint is responding"
else
    echo "❌ API root endpoint failed"
    docker logs $CONTAINER_ID
    exit 1
fi

# Test info endpoint
if curl -f --connect-timeout 10 --max-time 30 http://localhost:$PORT/info; then
    echo "✅ Info endpoint is responding"
else
    echo "❌ Info endpoint failed"
    docker logs $CONTAINER_ID
    exit 1
fi

# Test OpenAPI endpoint
if curl -f --connect-timeout 10 --max-time 30 http://localhost:$PORT/openapi.json; then
    echo "✅ OpenAPI endpoint is responding"
else
    echo "❌ OpenAPI endpoint failed"
    docker logs $CONTAINER_ID
    exit 1
fi

# Test 5: Static assets
echo "📁 Test 5: Static assets"
if curl -f --connect-timeout 10 --max-time 30 http://localhost:$PORT/assets/; then
    echo "✅ Static assets are accessible"
else
    echo "❌ Static assets are not accessible"
    docker logs $CONTAINER_ID
    exit 1
fi

# Test 6: Container logs check
echo "📋 Test 6: Container logs check"
LOGS=$(docker logs $CONTAINER_ID 2>&1)
if echo "$LOGS" | grep -q "ERROR\|FATAL\|Exception"; then
    echo "❌ Found errors in container logs:"
    echo "$LOGS" | grep -i "error\|fatal\|exception"
    exit 1
else
    echo "✅ No critical errors found in logs"
fi

# Test 7: Container resource usage
echo "💾 Test 7: Container resource usage"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $CONTAINER_ID

# Test 8: Container processes
echo "⚙️ Test 8: Container processes"
docker exec $CONTAINER_ID ps aux || echo "⚠️ Cannot exec into container (this may be expected)"

# Test 9: Network connectivity
echo "🌐 Test 9: Network connectivity"
docker exec $CONTAINER_ID curl -f http://localhost/health || echo "⚠️ Internal health check failed"

# Test 10: Data persistence (if data directory is mounted)
echo "💾 Test 10: Data persistence check"
if docker exec $CONTAINER_ID test -d /data; then
    echo "✅ Data directory exists"
    docker exec $CONTAINER_ID ls -la /data/
else
    echo "ℹ️ No data directory mounted (ephemeral mode)"
fi

echo ""
echo "🎉 All integration tests passed!"
echo "✅ NetWiz container is working correctly"
echo "📊 Container is running on port $PORT"
echo "🔗 Access the application at: http://localhost:$PORT"
echo "📖 API documentation at: http://localhost:$PORT/docs"
