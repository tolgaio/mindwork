# syntax=docker/dockerfile:1

FROM python:3.12-slim

# Install ffmpeg
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock* ./
COPY audio_chunker.py ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Default entrypoint
ENTRYPOINT ["uv", "run", "mindwork-transcribe"]
