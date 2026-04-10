FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency manifests first — this layer is cached until pyproject.toml
# or uv.lock changes, so rebuilds triggered by source-only edits skip uv sync.
COPY pyproject.toml uv.lock ./

# Install production dependencies (no dev extras) into a virtual env
RUN uv sync --no-dev --frozen

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

ENV PATH="/root/.local/bin:$PATH"

# Re-install uv in runtime stage (needed to run commands)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy the pre-built virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/pyproject.toml /app/uv.lock ./

# Copy application source (changes here do NOT bust the dependency cache)
COPY app ./app

# Expose API port
EXPOSE 8000

# Default command (will be overridden in compose.yaml)
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
