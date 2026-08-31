# ==============================================================================
# AGENTPAY Backend Production Dockerfile (Python 3.11 / FastAPI)
# ==============================================================================

FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build tools and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy requirements from agent-runtime app
COPY apps/agent-runtime/requirements.txt .

# Install dependencies into virtual environment or user location
RUN pip install --prefix=/install -r requirements.txt

# ------------------------------------------------------------------------------
# Final Runtime Stage
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runner

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/apps/agent-runtime \
    PORT=8000

# Install runtime system dependencies (curl for container healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root system user
RUN groupadd -r agentpay && useradd -r -g agentpay agentpay

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application source code
COPY apps/agent-runtime /app/apps/agent-runtime

# Set correct ownership
RUN chown -R agentpay:agentpay /app

USER agentpay

EXPOSE 8000

# Health check targeting AGENTPAY backend health endpoint
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

WORKDIR /app/apps/agent-runtime

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
