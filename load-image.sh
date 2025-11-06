#!/bin/bash
# Load Docker image from tar file and start container

TAR_FILE=$1

if [ -z "$TAR_FILE" ]; then
    echo "Usage: ./load-image.sh <image-file.tar>"
    echo "Example: ./load-image.sh ticketbroker_latest_20251027-104536.tar"
    exit 1
fi

if [ ! -f "$TAR_FILE" ]; then
    echo "Error: File $TAR_FILE not found"
    exit 1
fi

echo "Loading Docker image from $TAR_FILE..."
docker load < "$TAR_FILE"

echo "Starting dev container (separate from production)..."
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d

echo ""
echo "✅ Done! Dev version running on port 5001"
echo "Check status: docker-compose -f docker-compose.dev.yml ps"
echo "View logs: docker-compose -f docker-compose.dev.yml logs -f"
echo "Access: http://localhost:5001"
