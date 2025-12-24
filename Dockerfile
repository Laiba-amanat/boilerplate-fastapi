# Use official Python 3.11 slim image as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    TZ=Asia/Shanghai

# Switch to domestic mirror source for faster downloads
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files and install Python dependencies
COPY pyproject.toml ./
COPY README.md ./
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir . -i https://pypi.tuna.tsinghua.edu.cn/simple

# Copy project files
COPY . .

# Copy and set startup script permissions
COPY scripts/docker-entrypoint.sh /scripts/docker-entrypoint.sh
RUN chmod +x /scripts/docker-entrypoint.sh

# Create necessary directories
RUN mkdir -p /app/logs /app/static /app/migrations

# Note: Running as root user temporarily to avoid permission issues
# In production environment, it's recommended to configure appropriate user permissions

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Startup command
CMD ["/scripts/docker-entrypoint.sh"]
