FROM python:3.10-slim

# Install system dependencies needed for Scrapy
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy source code
COPY src/ ./src/
COPY scrapy.cfg ./
COPY main.py ./

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Default command - can be overridden
CMD ["dagster", "code-server", "start", "-h", "0.0.0.0", "-p", "4000", "-f", "definitions.py"]
