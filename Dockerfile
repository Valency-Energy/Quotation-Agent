FROM python:3.9-slim AS build

WORKDIR /app
# git and build-essential, two common libraries needed for installing Python dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# we can clean up the installations by removing the caches
#via apt-get clean and removing the updated package list via rm-rf /var/lib/apt/lists/*.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# ===== Final Stage =====
FROM python:3.12-slim
COPY --from=build /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]