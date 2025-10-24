#!/bin/bash

# Raspberry Pi Deployment Script for TicketBroker
# Usage: ./deploy-pi.sh [version]
# Example: ./deploy-pi.sh v1.2.3
# Example: ./deploy-pi.sh latest

set -e

echo "🚀 Deploying TicketBroker to Raspberry Pi..."

# Configuration
IMAGE_NAME="ghcr.io/magpern/ticketbroker"
CONTAINER_NAME="ticketbroker"
COMPOSE_FILE="docker-compose.pi.yml"

# Get version from argument or default to latest
VERSION=${1:-latest}
FULL_IMAGE_NAME="${IMAGE_NAME}:${VERSION}"

echo "📦 Deploying version: ${VERSION}"
echo "🐳 Image: ${FULL_IMAGE_NAME}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Update docker-compose file with specific version
echo "📝 Updating docker-compose file..."
sed -i "s|image: ghcr.io/magpern/ticketbroker:.*|image: ${FULL_IMAGE_NAME}|" ${COMPOSE_FILE}

# Pull the specified image
echo "📥 Pulling image: ${FULL_IMAGE_NAME}..."
docker pull ${FULL_IMAGE_NAME}

# Stop existing container if running
echo "🛑 Stopping existing container..."
docker-compose -f ${COMPOSE_FILE} down || true

# Start the new container
echo "▶️ Starting new container..."
docker-compose -f ${COMPOSE_FILE} up -d

# Wait for health check
echo "⏳ Waiting for application to be healthy..."
timeout=60
counter=0
while [ $counter -lt $timeout ]; do
    if docker-compose -f ${COMPOSE_FILE} ps | grep -q "healthy"; then
        echo "✅ Application is healthy!"
        break
    fi
    echo "Waiting... ($counter/$timeout)"
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    echo "⚠️ Health check timeout. Check logs:"
    docker-compose -f ${COMPOSE_FILE} logs
    exit 1
fi

# Show status
echo "📊 Container status:"
docker-compose -f ${COMPOSE_FILE} ps

echo "🎉 Deployment complete!"
echo "🌐 Application should be available at: http://your-pi-ip:5000"
echo "📋 Deployed version: ${VERSION}"
