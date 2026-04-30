# 🛡️ AI Email Security Detector

An AI-powered email security detector that identifies spam, phishing, and AI-generated malicious emails with 95%+ accuracy.

## Quick Start

### Prerequisites

- **Python 3.11+** (for local run)
- **Docker & Docker Compose** (for containerised run)
- **Git**

### Clone the repo

```bash
git clone https://github.com/ak7173897/Emails_detector.git
cd Emails_detector/email-detector
```

---

### Option A — Run locally with `make` (Linux / macOS)

```bash
# 1. Install dependencies into a virtual environment
make install

# 2. Start the development server (http://localhost:5000)
make dev

# 3. (Optional) Run a quick sample-usage demo
make sample

# 4. (Optional) Run the model self-test
make test
```

### Option B — Run locally without `make`

```bash
cd email-detector

# Create & activate a virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the Flask development server
export FLASK_APP=src.wsgi:application
export FLASK_ENV=development
export SECRET_KEY="dev-secret-key-32-characters!!"
flask run --host=127.0.0.1 --port=5000
```

Open <http://localhost:5000> in your browser.

### Option C — Run with Docker Compose (recommended for production)

```bash
cd email-detector

# Copy and edit the environment file (set SECRET_KEY)
cp .env.example .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env

# Build and start
docker-compose up --build -d

# Check health
curl http://localhost:5000/health
```

### Option D — Windows users

```bat
cd email-detector

REM Local run (requires .venv already set up)
run-local.bat

REM Docker run
run-docker.bat
```

---

## Quick API test (server must be running)

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "URGENT: You have won $1,000,000! Click here to claim your prize NOW!"}'
```

---

## Project layout

```
Emails_detector/
└── email-detector/       # Main application
    ├── src/              # Flask backend & ML code
    ├── models/           # Pre-trained ML model (.pkl)
    ├── templates/        # HTML templates
    ├── static/           # CSS / JS assets
    ├── dataset/          # Training data
    ├── scripts/          # Helper shell scripts
    ├── requirements.txt  # Python dependencies
    ├── Makefile          # Common developer commands
    ├── Dockerfile        # Container definition
    ├── docker-compose.yml
    ├── sample_usage.py   # Standalone demo (no server needed)
    └── README.md         # Full documentation
```

See [`email-detector/README.md`](email-detector/README.md) for the full documentation including API reference, configuration options, and architecture details.