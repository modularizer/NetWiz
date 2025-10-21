#!/bin/sh
set -e

echo "🚀 Starting NetWiz Docker-in-Docker container"

# Ensure Docker daemon configuration exists with custom data directory
mkdir -p /etc/docker
mkdir -p /app/docker-data
mkdir -p /etc/containerd

# Configure containerd
cat >/etc/containerd/config.toml <<'EOF'
version = 2
root = "/var/lib/containerd"
state = "/run/containerd"
[grpc]
  address = "/run/containerd/containerd.sock"
  uid = 0
  gid = 0
[ttrpc]
  address = "/run/containerd/containerd.sock.ttrpc"
  uid = 0
  gid = 0
[debug]
  address = ""
  uid = 0
  gid = 0
  level = ""
[metrics]
  address = ""
  grpc_histogram = false
[cgroup]
  path = ""
[timeouts]
  "io.containerd.timeout.shim.cleanup" = "5s"
  "io.containerd.timeout.shim.load" = "5s"
  "io.containerd.timeout.shim.shutdown" = "3s"
  "io.containerd.timeout.task.state" = "2s"
[plugins]
  [plugins."io.containerd.gc.v1.scheduler"]
    pause_threshold = 0.02
    deletion_threshold = 0
    mutation_threshold = 100
    schedule_delay = "0s"
    startup_delay = "100ms"
  [plugins."io.containerd.grpc.v1.cri"]
    disable_tcp_service = true
    stream_server_address = "127.0.0.1"
    stream_server_port = "0"
    stream_idle_timeout = "4h0m0s"
    enable_selinux = false
    selinux_category_range = 1024
    sandbox_image = "registry.k8s.io/pause:3.9"
    stats_collect_period = 10
    systemd_cgroup = false
    enable_tls_streaming = false
    max_container_log_line_size = 16384
    disable_cgroup = false
    disable_apparmor = false
    disable_hugetlb_controller = true
    ignore_image_defined_volumes = false
    [plugins."io.containerd.grpc.v1.cri".containerd]
      snapshotter = "overlayfs"
      default_runtime_name = "runc"
      no_pivot = false
      disable_snapshot_annotations = true
      discard_unpacked_layers = false
    [plugins."io.containerd.grpc.v1.cri".containerd.runtimes]
      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
        runtime_type = "io.containerd.runc.v2"
        runtime_engine = ""
        runtime_root = ""
        privileged_without_host_devices = false
        base_runtime_spec = ""
        [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
          SystemdCgroup = false
EOF

# Optimize Docker daemon configuration for faster startup
cat >/etc/docker/daemon.json <<'EOF'
{
  "hosts": ["unix:///var/run/docker.sock"],
  "log-level": "warn",
  "live-restore": true,
  "max-concurrent-downloads": 3,
  "max-concurrent-uploads": 5,
  "shutdown-timeout": 15,
  "default-address-pools": [
    {
      "base": "172.17.0.0/12",
      "size": 16
    }
  ]
}
EOF
echo "📁 Configured Docker to use custom data directory: /app/docker-data"

# Clean up any existing Docker processes
echo "🧹 Cleaning up any existing Docker processes..."
pkill dockerd 2>/dev/null || true
pkill containerd 2>/dev/null || true
pkill containerd-shim 2>/dev/null || true
sleep 3

# Force kill any remaining processes
pkill -9 dockerd 2>/dev/null || true
pkill -9 containerd 2>/dev/null || true
pkill -9 containerd-shim 2>/dev/null || true
sleep 2

# Start Docker daemon
echo "🐳 Starting Docker daemon..."
unset DOCKER_TLS_CERTDIR  # Ensure TLS is off
/usr/local/bin/dockerd 2>&1 | tee /var/log/dockerd.log &
D_PID=$!

# Wait for dockerd (and bail if it died)
echo "⏳ Waiting for Docker daemon to be ready..."
for i in $(seq 1 60); do
  kill -0 "$D_PID" 2>/dev/null || { echo "❌ dockerd crashed"; tail -n 200 /var/log/dockerd.log; exit 1; }
  docker info >/dev/null 2>&1 && break
  sleep 2
done
echo "✅ Docker daemon ready"

# Load cached images from tar files
echo "📦 Loading cached images from tar files..."
if [ -f "/app/netwiz-backend.tar" ]; then
    echo "📥 Loading netwiz-backend..."
    docker load -i /app/netwiz-backend.tar
fi
if [ -f "/app/netwiz-frontend.tar" ]; then
    echo "📥 Loading netwiz-frontend..."
    docker load -i /app/netwiz-frontend.tar
fi
if [ -f "/app/netwiz-nginx.tar" ]; then
    echo "📥 Loading netwiz-nginx..."
    docker load -i /app/netwiz-nginx.tar
fi
if [ -f "/app/mongo.tar" ]; then
    echo "📥 Loading mongo..."
    docker load -i /app/mongo.tar
fi

echo "✅ All cached images loaded"

# Set up environment
export COMPOSE_PROJECT_NAME=netwiz

# Check if /data is mounted from host and use it for MongoDB
if [ -d "/data" ] && [ -w "/data" ]; then
    echo "📁 Found mounted /data directory, using it for MongoDB"
    export MONGODB_DATA_PATH="/data/mongodb"
else
    echo "📁 Using Docker volume for MongoDB data"
    export MONGODB_DATA_PATH="mongodb_data"
fi

# Create MongoDB data directory if MONGODB_DATA_PATH is a host path
if [ "$MONGODB_DATA_PATH" != "mongodb_data" ] && [ ! -d "$MONGODB_DATA_PATH" ]; then
    echo "📁 Creating MongoDB data directory: $MONGODB_DATA_PATH"
    mkdir -p "$MONGODB_DATA_PATH"
    echo "✅ MongoDB data directory created"
fi

# Check if .env file is mounted from host
if [ -f "/app/backend.env" ]; then
    echo "📄 Using mounted .env file: /app/backend.env"
    export BACKEND_ENV_FILE="/app/backend.env"
else
    echo "📄 Using default backend configuration"
    unset BACKEND_ENV_FILE
fi

# Set up signal handling for graceful shutdown
cleanup() {
    echo "🛑 Shutting down gracefully..."
    # Stop Docker Compose services first with timeout
    echo "📦 Stopping Docker Compose services..."
    timeout 5 docker compose down 2>/dev/null || {
        echo "⚠️ Docker Compose shutdown timed out, forcing stop..."
        docker compose kill 2>/dev/null || true
        docker compose rm -f 2>/dev/null || true
    }
    # Then stop the Docker daemon
    echo "🐳 Stopping Docker daemon..."
    kill $D_PID 2>/dev/null || true
    # Wait a moment for processes to clean up
    sleep 3
    # Force kill any remaining Docker processes
    echo "🔪 Force killing remaining Docker processes..."
    pkill -9 dockerd 2>/dev/null || true
    pkill -9 docker-compose 2>/dev/null || true
    pkill -9 containerd 2>/dev/null || true
    pkill -9 containerd-shim 2>/dev/null || true
    echo "✅ Shutdown complete"
    exit 0
}

# Set up trap for signals
trap cleanup SIGTERM SIGINT

# Also set up cleanup on script exit
trap cleanup EXIT

# Start the application stack with optimized settings
echo "🚀 Starting NetWiz application stack..."
# Use reduced timeouts for faster startup
DOCKER_COMPOSE_HTTP_TIMEOUT=30 docker compose up &
COMPOSE_PID=$!

# Wait for Docker Compose to finish or be interrupted
wait $COMPOSE_PID
COMPOSE_EXIT_CODE=$?

echo "📦 Docker Compose exited with code: $COMPOSE_EXIT_CODE"

# Clean up will be handled by EXIT trap
