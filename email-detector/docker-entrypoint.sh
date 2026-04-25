#!/bin/bash
# ==============================================================================
# Docker Entrypoint Script for AI Email Security Detector
# ==============================================================================
# Handles initialization, model training, and graceful startup
# ==============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Redis is available
wait_for_redis() {
    print_status "Waiting for Redis to be ready..."
    
    # Extract Redis connection details from REDIS_URL
    if [ -n "$REDIS_URL" ]; then
        # Parse Redis URL for host and port
        REDIS_HOST=$(echo $REDIS_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
        REDIS_PORT=$(echo $REDIS_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        if [ -z "$REDIS_HOST" ]; then
            REDIS_HOST="redis"
        fi
        
        if [ -z "$REDIS_PORT" ]; then
            REDIS_PORT="6379"
        fi
        
        # Wait for Redis to be responsive
        for i in {1..30}; do
            if nc -z "$REDIS_HOST" "$REDIS_PORT" 2>/dev/null; then
                print_success "Redis is ready at $REDIS_HOST:$REDIS_PORT"
                return 0
            fi
            print_status "Redis not ready yet (attempt $i/30)..."
            sleep 2
        done
        
        print_error "Redis is not responding after 60 seconds"
        return 1
    else
        print_warning "REDIS_URL not set, skipping Redis check"
    fi
}

# Function to check if model exists
check_model() {
    if [ -f "/app/models/email_classifier.pkl" ]; then
        print_success "ML model found at /app/models/email_classifier.pkl"
        return 0
    else
        print_warning "ML model not found, will train on startup"
        return 1
    fi
}

# Function to train the ML model
train_model() {
    print_status "Training ML model..."
    
    cd /app
    
    if python -m src.utils.train_model; then
        print_success "ML model training completed successfully"
    else
        print_error "ML model training failed"
        exit 1
    fi
}

# Function to validate configuration
validate_config() {
    print_status "Validating configuration..."
    
    # Check required environment variables
    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "change-this-to-a-secure-random-key-in-production" ]; then
        print_error "SECRET_KEY not set or using default value. This is a security risk!"
        exit 1
    fi
    
    # Check secret key length
    if [ ${#SECRET_KEY} -lt 32 ]; then
        print_error "SECRET_KEY must be at least 32 characters long"
        exit 1
    fi
    
    print_success "Configuration validation passed"
}

# Function to set up directories and permissions
setup_directories() {
    print_status "Setting up directories and permissions..."
    
    # Ensure directories exist
    mkdir -p /app/logs /app/models /app/uploads /app/feedback
    
    # Set permissions (already owned by appuser)
    chmod 750 /app/logs /app/models /app/uploads /app/feedback
    
    print_success "Directory setup completed"
}

# Function to run security checks
security_check() {
    print_status "Running security checks..."
    
    # Check if running as root (should not be)
    if [ "$(id -u)" = "0" ]; then
        print_error "Container should not run as root user!"
        exit 1
    fi
    
    # Verify Python dependencies
    if ! python -c "import flask, sklearn, bleach, flask_talisman, flask_limiter" 2>/dev/null; then
        print_error "Required security dependencies not installed"
        exit 1
    fi
    
    print_success "Security checks passed"
}

# Function to display startup information
show_startup_info() {
    print_status "==================================="
    print_status "AI Email Security Detector"
    print_status "==================================="
    print_status "Version: ${VERSION:-1.0.0}"
    print_status "Environment: ${FLASK_ENV:-production}"
    print_status "User: $(whoami)"
    print_status "Working Directory: $(pwd)"
    print_status "Python Version: $(python --version)"
    print_status "==================================="
}

# Main initialization function
init() {
    show_startup_info
    security_check
    validate_config
    setup_directories
    wait_for_redis
    
    # Train model if it doesn't exist
    if ! check_model; then
        train_model
    fi
    
    print_success "Initialization completed successfully"
}

# Signal handlers for graceful shutdown
cleanup() {
    print_status "Received shutdown signal, cleaning up..."
    # Add any cleanup tasks here
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Main execution
case "$1" in
    "init-only")
        init
        print_success "Initialization complete, exiting"
        ;;
    "train-model")
        train_model
        ;;
    "gunicorn"|"python")
        init
        print_status "Starting application server..."
        exec "$@"
        ;;
    "bash"|"sh")
        print_status "Starting interactive shell..."
        exec "$@"
        ;;
    *)
        init
        print_status "Starting application with default command..."
        exec gunicorn -c gunicorn_config.py wsgi:application
        ;;
esac