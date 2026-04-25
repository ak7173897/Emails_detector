#!/bin/bash
# Build and Run Email Security Detector (Single Container)

echo "Building Email Security Detector (Single Container)..."

# Change to project root
cd "$(dirname "$0")/.."

# Build the Docker image
docker build -f Dockerfile -t email-detector:latest .

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo ""
    echo "To run the container, use:"
    echo "  ./run-docker.sh"
else
    echo "Build failed!"
    exit 1
fi
