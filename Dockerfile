FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# ── Runtime ───────────────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/pyproject.toml /app/uv.lock ./
COPY app ./app

# SQLite DB lives in /app/data (mounted as a volume)
RUN mkdir -p /app/data
ENV DATABASE_URL=sqlite+aiosqlite:///data/fitlog.db

EXPOSE 8000
CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
