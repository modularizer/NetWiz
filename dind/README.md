# Docker-in-Docker Configuration

This directory contains all Docker-in-Docker related files for NetWiz.

## Scripts (Resilient - callable from any directory)

All shell scripts automatically detect their location and change to the project root directory, making them callable from anywhere:

- **`build.sh`** - Build all Docker containers
- **`build-and-test.sh`** - Build with temporary tag, test, and retag if tests pass
- **`test.sh`** - Run integration tests on a container
- **`push.sh`** - Push containers to registry
- **`start.sh`** - Start NetWiz locally

## Usage Examples

### From project root:
```bash
./dind/build.sh main
./dind/test.sh netwiz:main
./dind/push.sh main ghcr.io/modularizer
./dind/start.sh 8080 ./data ./backend/.env
```

### From any directory:
```bash
/path/to/NetWiz/dind/build.sh main
/path/to/NetWiz/dind/test.sh netwiz:main
/path/to/NetWiz/dind/push.sh main ghcr.io/modularizer
```

### From dind directory:
```bash
cd dind
./build.sh main
./test.sh netwiz:main
./push.sh main ghcr.io/modularizer
```

## Architecture

The DinD container uses **pre-pulled GHCR images**:

1. **Build Phase**: `build.sh` builds all service images and pushes them to GHCR
2. **DinD Build**: DinD container pulls images from GHCR during build time
3. **Runtime**: Docker Compose uses the pre-pulled images (no network calls needed)

### Benefits:
- ✅ **Smaller DinD Container**: No source code copying
- ✅ **Faster Startup**: No building inside DinD container
- ✅ **Security**: No Docker socket sharing needed
- ✅ **Self-contained**: Everything needed is included

### Requirements:
- 🔧 **Privileged Mode**: DinD container requires `--privileged` flag
- 🐧 **Linux Kernel**: Requires access to host kernel modules
- 🐳 **Docker**: Host system must have Docker installed

### Security Features:
- 🔒 **Unix Socket Only**: Docker daemon only binds to Unix socket (no TCP)
- 🛡️ **No Network Exposure**: Docker API not accessible over network
- 🔐 **Isolated Daemon**: DinD runs its own Docker daemon internally
- ⚠️ **Privileged Required**: Still requires `--privileged` for kernel access

## Dockerfile Requirements

The `Dockerfile` must be built from the project root directory:

```bash
docker build -f dind/Dockerfile -t netwiz:tag .
```

## Environment Configuration

### Backend .env File Support

The backend container supports mounting a custom `.env` file for configuration:

1. **Create a `.env` file** (copy from `backend/env.example`):
   ```bash
   cp backend/env.example backend/.env
   # Edit backend/.env with your settings
   ```

2. **Start with custom .env file**:
   ```bash
   ./dind/start.sh 8080 ./data ./backend/.env
   ```

3. **Default behavior**: If no `.env` file is provided, the backend uses built-in defaults.

### Environment Variables

Key backend environment variables:
- `MONGODB_URI` - MongoDB connection string
- `JWT_SECRET_KEY` - JWT signing secret (change in production!)
- `JWT_REFRESH_SECRET_KEY` - JWT refresh secret (change in production!)
- `PASSWORD_PEPPER` - Password hashing pepper (change in production!)
- `ADMIN_TEMP_PASSWORD` - Initial admin password
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `CORS_ORIGINS` - Allowed CORS origins

## Files

- **`Dockerfile`** - Docker-in-Docker container definition (must build from project root)
- **`docker-compose.yml`** - Docker Compose configuration for DinD setup
- **`dind-internal-start.sh`** - Internal startup script for DinD container
- **`build.sh`** - Script to build all Docker containers
- **`build-and-test.sh`** - Build, test, and retag script
- **`test.sh`** - Integration test script
- **`push.sh`** - Script to push containers to registry
- **`start.sh`** - Script to start NetWiz locally

## Service Dockerfiles

The individual service Dockerfiles remain in their respective directories:
- `backend/Dockerfile` - Backend service
- `frontend/Dockerfile` - Frontend service
- `nginx/Dockerfile` - Nginx service
