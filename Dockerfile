# Use Python 3.11 slim image with build arguments for platform
# This supports both amd64 (Raspberry Pi 4/5) and arm64 (Raspberry Pi 4/5)
ARG TARGETPLATFORM
ARG BUILDPLATFORM
FROM --platform=$BUILDPLATFORM python:3.11-slim AS build

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data and logs directories
RUN mkdir -p /data /logs

# Set environment variables
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV DATABASE_URL=sqlite:////data/ticketbroker.db

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app /data /logs
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Starting TicketBroker..."\n\
echo "Initializing database..."\n\
flask db upgrade\n\
echo "Starting application..."\n\
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 run:app' > /app/start.sh && \
    chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]
