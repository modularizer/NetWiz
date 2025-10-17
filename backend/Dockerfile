FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set default environment variables (can be overridden)
ENV ENVIRONMENT=production
ENV DEBUG=false
ENV HOST=0.0.0.0
ENV PORT=5000
ENV RELOAD=false
ENV LOG_LEVEL=INFO
ENV MONGODB_URI=mongodb://mongodb:27017/netwiz
ENV MONGODB_DATABASE=netwiz
ENV CORS_ORIGINS=http://frontend:3000,http://localhost:3000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run the application using environment variables
CMD ["sh", "-c", "uvicorn main:app --host ${HOST} --port ${PORT} --reload=${RELOAD}"]
