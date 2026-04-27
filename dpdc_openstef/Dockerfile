# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Install Poetry deps into the system Python (no virtualenv in containers)
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for some Python packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better layer caching
COPY requirements.txt pyproject.toml install_deps.sh ./
# Copy lock file only when it exists
COPY poetry.loc[k] ./

# Install Python dependencies
RUN sh install_deps.sh

# Copy application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application (LOG_LEVEL controls verbosity)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8080 --reload --log-level ${LOG_LEVEL:-info}"]
