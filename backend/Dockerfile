# Backend Dockerfile for Hot Take Generator
# Multi-stage build for smaller, more secure images

# ============================================
# Builder Stage: Install dependencies
# ============================================
FROM python:3.14-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_CACHE_DIR=/tmp/uv-cache

# Install build dependencies and uv
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .python-version uv.lock ./

# Install dependencies with uv sync
RUN uv sync --frozen

# ============================================
# Runtime Stage: Slim production image
# ============================================
FROM python:3.14-slim AS runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install runtime dependencies (curl for health checks and uv)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy uv-managed Python from builder (required for venv symlinks)
COPY --from=builder /root/.local/share/uv /root/.local/share/uv

# Copy virtual environment from builder
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Grant app user access to uv Python installation
RUN chmod a+rx /root && chmod -R a+rX /root/.local

# Copy application code
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check - using /ready to verify environment configuration
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ready || exit 1

# Start the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
