# ==============================================================================
# AI Email Security Detector - Production Dockerfile
# ==============================================================================
# Multi-stage build for optimized production container
# Security-hardened with non-root user and minimal attack surface
# ==============================================================================

# Build stage
FROM python:3.11-slim-bullseye AS builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=1.0.0
ARG VCS_REF

# Add labels for container metadata
LABEL maintainer="Email Security Detector Team" \
      org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="email-security-detector" \
      org.label-schema.description="AI-powered email security detector" \
      org.label-schema.version=$VERSION \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.schema-version="1.0"

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ==============================================================================
# Production stage
FROM python:3.11-slim-bullseye AS production

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies only (curl for health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Set working directory
WORKDIR /app

# Create necessary directories with correct permissions
RUN mkdir -p /app/models /app/static /app/templates && \
    chown -R appuser:appuser /app

# Copy application files with correct ownership
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser docker-entrypoint.sh .
COPY --chown=appuser:appuser requirements.txt .
COPY --chown=appuser:appuser static/ ./static/
COPY --chown=appuser:appuser templates/ ./templates/
COPY --chown=appuser:appuser models/ ./models/
# Note: dataset/ is not needed in production image (training done separately)
COPY --chown=appuser:appuser config/gunicorn_config.py ./gunicorn_config.py

# Set secure file permissions
RUN chmod 755 /app && \
    chmod 750 /app/models && \
    find /app/src -type f -name "*.py" -exec chmod 644 {} \; && \
    find /app/static -type f -exec chmod 644 {} \; 2>/dev/null || true && \
    find /app/templates -type f -exec chmod 644 {} \; 2>/dev/null || true && \
    chmod +x /app/docker-entrypoint.sh 2>/dev/null || true

# Switch to non-root user
USER appuser

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    FLASK_APP=src.wsgi:application \
    FLASK_ENV=production

# Health check - validates both HTTP response and model loading
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -sf http://localhost:5000/health | grep -q '"model_loaded":true' || exit 1

# Expose port
EXPOSE 5000

# Use gunicorn directly with optimized settings
# - 4 workers for better concurrency
# - 120s timeout for ML predictions
# - Log to stdout/stderr for Docker logging
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--worker-class", "gevent", \
     "--worker-connections", "1000", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "src.wsgi:application"]