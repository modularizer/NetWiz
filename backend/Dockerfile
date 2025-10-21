FROM python:3.11-slim

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

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package in editable mode to make scripts available
RUN pip install -e .

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
