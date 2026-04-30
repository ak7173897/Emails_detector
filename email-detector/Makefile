# ==============================================================================
# AI Email Security Detector — Developer Makefile
# ==============================================================================
# Usage:
#   make install      Create venv and install all Python dependencies
#   make dev          Start the Flask development server (http://localhost:5000)
#   make run          Start with Gunicorn (production-like, requires SECRET_KEY)
#   make sample       Run the standalone sample-usage demo (no server needed)
#   make test         Run the model self-test
#   make docker-build Build the Docker image
#   make docker-run   Run the Docker container
#   make clean        Remove the virtual environment and cache files
# ==============================================================================

PYTHON     := python3
VENV       := .venv
PIP        := $(VENV)/bin/pip
FLASK      := $(VENV)/bin/flask
PYTHON_V   := $(VENV)/bin/python

.DEFAULT_GOAL := help

# ── Help ──────────────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "  AI Email Security Detector"
	@echo ""
	@echo "  make install       Create .venv and install dependencies"
	@echo "  make dev           Run Flask dev server  (http://localhost:5000)"
	@echo "  make run           Run Gunicorn server   (http://localhost:5000)"
	@echo "  make sample        Run standalone email-detection demo"
	@echo "  make test          Run the model self-test"
	@echo "  make docker-build  Build Docker image"
	@echo "  make docker-run    Run Docker container"
	@echo "  make clean         Remove .venv and __pycache__"
	@echo ""

# ── Install ───────────────────────────────────────────────────────────────────
.PHONY: install
install: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo ""
	@echo "  Dependencies installed. Activate the venv with:"
	@echo "    source $(VENV)/bin/activate"
	@echo ""

# ── Development server ────────────────────────────────────────────────────────
# NOTE: the SECRET_KEY below is a placeholder only for local development.
#       Do NOT use it in any shared or production environment.
.PHONY: dev
dev: install
	FLASK_APP=src.wsgi:application \
	FLASK_ENV=development \
	SECRET_KEY="dev-secret-key-32-characters!!" \
	$(FLASK) run --host=127.0.0.1 --port=5000

# ── Production-like server (Gunicorn) ─────────────────────────────────────────
.PHONY: run
run: install
	@if [ -z "$$SECRET_KEY" ]; then \
	  echo "ERROR: SECRET_KEY environment variable is not set."; \
	  echo "  export SECRET_KEY=\$$(openssl rand -hex 32)"; \
	  exit 1; \
	fi
	FLASK_ENV=production \
	$(VENV)/bin/gunicorn \
	  --bind 0.0.0.0:5000 \
	  --workers 2 \
	  --timeout 120 \
	  --access-logfile - \
	  --error-logfile - \
	  src.wsgi:application

# ── Standalone sample usage (no server required) ──────────────────────────────
.PHONY: sample
sample: install
	$(PYTHON_V) sample_usage.py

# ── Model self-test ───────────────────────────────────────────────────────────
.PHONY: test
test: install
	$(PYTHON_V) -m src.utils.test_model

# ── Docker ────────────────────────────────────────────────────────────────────
.PHONY: docker-build
docker-build:
	docker build -t email-detector:latest .

.PHONY: docker-run
docker-run:
	@if [ -z "$$SECRET_KEY" ]; then \
	  SECRET_KEY="$$(openssl rand -hex 32)"; \
	else \
	  SECRET_KEY="$$SECRET_KEY"; \
	fi; \
	docker run -d \
	  --name email-detector \
	  -p 5000:5000 \
	  -e FLASK_ENV=production \
	  -e SECRET_KEY="$$SECRET_KEY" \
	  -e LOG_LEVEL=INFO \
	  --restart unless-stopped \
	  email-detector:latest && \
	echo "Container started → http://localhost:5000"

# ── Clean ─────────────────────────────────────────────────────────────────────
.PHONY: clean
clean:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Cleaned."
