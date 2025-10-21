#!/bin/sh

set -e

echo "Starting Docker daemon..."
dockerd-entrypoint.sh &

# Wait for Docker daemon to be ready
echo "Waiting for Docker daemon to be ready..."
while ! docker info >/dev/null 2>&1; do
  sleep 1
done
echo "Docker daemon is ready!"

# Clean up any existing NetWiz containers
echo "Cleaning up existing NetWiz containers..."
docker stop $(docker ps -q --filter "name=netwiz-") 2>/dev/null || true
docker rm $(docker ps -aq --filter "name=netwiz-") 2>/dev/null || true

# Start the services using docker-compose with internal Docker daemon
echo "Starting NetWiz services..."
MONGODB_DATA_PATH=/data/mongodb docker-compose -f docker-compose.dind.yml up
