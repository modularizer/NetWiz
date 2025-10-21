# Multi-stage build for smaller final image
FROM python:3.11-slim AS builder

# Set build arguments
ARG ENVIRONMENT=production
ARG GIT_COMMIT_HASH=""
ARG GIT_COMMIT_SHORT=""
ARG GIT_BRANCH=""
ARG GIT_TAG=""
ARG BUILD_TIME=""
ARG BUILD_REF=""
ARG BUILD_SHA=""

# Set Python environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install --no-cache-dir .

# Second stage: runtime image
FROM python:3.11-slim AS runtime

# Set build arguments for runtime
ARG ENVIRONMENT=production
ARG GIT_COMMIT_HASH=""
ARG GIT_COMMIT_SHORT=""
ARG GIT_BRANCH=""
ARG GIT_TAG=""
ARG BUILD_TIME=""
ARG BUILD_REF=""
ARG BUILD_SHA=""

# Set Python environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create a default .env file if none is mounted
RUN echo "# Default environment variables\n\
ENVIRONMENT=production\n\
HOST=0.0.0.0\n\
PORT=5000\n\
MONGODB_URI=mongodb://admin:password@mongodb:27017/netwiz?authSource=admin\n\
MONGODB_DATABASE=netwiz\n\
CORS_ORIGINS=*\n\
LOG_LEVEL=INFO\n\
LOG_FORMAT=json\n\
API_PREFIX=/api\n\
JWT_SECRET_KEY=your-secret-key-change-in-production\n\
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-change-in-production\n\
JWT_ALGORITHM=HS256\n\
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30\n\
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7\n\
PASSWORD_PEPPER=another-secret-change-me\n\
ADMIN_TEMP_PASSWORD=admin" > /app/.env

# Create git metadata file
RUN echo "{\n\
  \"commit_hash\": \"${GIT_COMMIT_HASH}\",\n\
  \"commit_short\": \"${GIT_COMMIT_SHORT}\",\n\
  \"branch\": \"${GIT_BRANCH}\",\n\
  \"tag\": \"${GIT_TAG}\",\n\
  \"build_time\": \"${BUILD_TIME}\",\n\
  \"build_ref\": \"${BUILD_REF}\",\n\
  \"build_sha\": \"${BUILD_SHA}\"\n\
}" > /app/netwiz_backend/git_metadata.json

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check (requires PORT env var to be set)
HEALTHCHECK --interval=30s --timeout=30s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5000}/health || exit 1

# Run the application using the installed script
CMD ["netwiz-backend"]
