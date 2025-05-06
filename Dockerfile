# === Build Stage ===
FROM python:3.9-slim AS build
WORKDIR /app
# Install system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# Copy UV binary from official image
COPY --from=ghcr.io/astral-sh/uv:0.6.13 /uv /uvx /bin/
# Copy requirements
COPY requirements.txt .
# Install dependencies directly using UV
RUN uv pip install --system -r requirements.txt \
    && pip install --no-cache-dir uvicorn

# === Final Stage ===
FROM python:3.9-slim
# Environment setup
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set working directory
WORKDIR /app
# Copy packages from build stage
COPY --from=build /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
# Copy app source code
COPY . .
# Expose FastAPI port
EXPOSE 8000
# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]