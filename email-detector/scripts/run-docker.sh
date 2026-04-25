#!/bin/bash
# Run Email Security Detector (Single Container)

echo "Starting Email Security Detector..."

# Change to project root
cd "$(dirname "$0")/.."

# Build image if missing
if ! docker image inspect email-detector:latest >/dev/null 2>&1; then
  echo "Docker image not found. Building image first..."
  docker build -f Dockerfile -t email-detector:latest .
  if [ $? -ne 0 ]; then
    echo "Image build failed!"
    exit 1
  fi
fi

# Stop and remove any existing container
docker stop email-detector 2>/dev/null
docker rm email-detector 2>/dev/null

# Generate a random secret key
SECRET_KEY=$(openssl rand -hex 32)

# Run the container
docker run -d \
  --name email-detector \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY="$SECRET_KEY" \
  -e CONFIDENCE_THRESHOLD=70.0 \
  -e MAX_EMAIL_LENGTH=50000 \
  -e LOG_LEVEL=INFO \
  --restart unless-stopped \
  email-detector:latest

if [ $? -eq 0 ]; then
    echo ""
    echo "Container started successfully!"
    echo ""
    echo "Access the application at: http://localhost:5000"
    echo ""
    echo "To view logs:"
    echo "  docker logs -f email-detector"
    echo ""
    echo "To stop the container:"
    echo "  docker stop email-detector"
else
    echo "Failed to start container!"
    exit 1
fi
