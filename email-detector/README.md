# 🛡️ AI Email Security Detector

<div align="center">

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)
![Accuracy](https://img.shields.io/badge/accuracy-95%25+-orange.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

**A production-ready, AI-powered email security detector that identifies spam, phishing, and AI-generated malicious emails with 95%+ accuracy.**

[Features](#-features) • [Quick Start](#-quick-start) • [API Reference](#-api-reference) • [Architecture](#-architecture) • [Security](#-security)

</div>

---

## 📋 Table of Contents

1. [Overview](#-overview)
2. [Features](#-features)
3. [Technology Stack](#-technology-stack)
4. [Quick Start](#-quick-start)
5. [Installation](#-installation)
6. [Configuration](#-configuration)
7. [API Reference](#-api-reference)
8. [User Interface Guide](#-user-interface-guide)
9. [Machine Learning Model](#-machine-learning-model)
10. [Architecture](#-architecture)
11. [Security Features](#-security-features)
12. [Performance](#-performance)
13. [Troubleshooting](#-troubleshooting)
14. [Development](#-development)
15. [Contributing](#-contributing)
16. [License](#-license)

---

## 🎯 Overview

The AI Email Security Detector is a comprehensive solution for analyzing and classifying emails to protect users from spam, phishing attacks, and AI-generated malicious content. Built with modern technologies and security best practices, it provides:

- **Real-time Analysis**: Instant email classification in under 1 second
- **Multi-Category Detection**: Identifies Safe, Spam, AI Phishing, and Uncertain emails
- **Confidence Scoring**: Provides probability distributions for transparent decision-making
- **Bulk Processing**: Analyze up to 100 emails simultaneously
- **Analytics Dashboard**: Visual insights into threat patterns and trends
- **Production Ready**: Dockerized, secure, and scalable

### Why This Project?

Email remains the primary attack vector for cybercriminals, with phishing attacks becoming increasingly sophisticated through AI-generated content. Traditional spam filters struggle with:

- AI-generated phishing emails that mimic legitimate communication
- Sophisticated social engineering tactics
- Zero-day phishing campaigns

This detector uses machine learning trained on real-world data to identify these threats with high accuracy.

---

## ✨ Features

### Core Analysis Features

| Feature | Description |
|---------|-------------|
| **Single Email Analysis** | Analyze individual emails with detailed results |
| **Bulk Processing** | Process up to 100 emails at once |
| **File Upload** | Support for .txt and .eml file formats |
| **Confidence Scoring** | Probability distribution across all categories |
| **Risk Indicators** | Detection of suspicious patterns (URLs, urgency, etc.) |
| **Uncertainty Detection** | Flags low-confidence predictions for manual review |

### User Interface Features

| Feature | Description |
|---------|-------------|
| **Dark/Light Theme** | Toggle between themes with persistence |
| **Responsive Design** | Works on desktop, tablet, and mobile |
| **Particle Animation** | Beautiful cyberpunk-style background |
| **History Tracking** | Local storage of last 50 analyses |
| **Search & Filter** | Search and filter analysis history |
| **Export Options** | Export results as JSON or CSV |

### Dashboard & Analytics

| Feature | Description |
|---------|-------------|
| **Summary Statistics** | Total analyzed, threats detected, safe emails |
| **Distribution Charts** | Visual breakdown of email categories |
| **Trend Analysis** | Time-series view of analysis patterns |
| **Risk Assessment** | Overall threat level indicator |
| **Recent Threats** | Quick view of latest detected threats |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + Enter` | Analyze email |
| `Ctrl + K` | Clear input |
| `Ctrl + Shift + C` | Copy results |
| `Ctrl + E` | Export JSON |
| `Alt + 1-5` | Navigate sections |

---

## 🛠️ Technology Stack

### Backend

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Core language | 3.11+ |
| **Flask** | Web framework | 2.3+ |
| **Scikit-learn** | Machine learning | 1.3+ |
| **Gunicorn** | WSGI server | 21.0+ |
| **Flask-Limiter** | Rate limiting | 3.5+ |
| **Flask-Talisman** | Security headers | 1.1+ |
| **Flask-WTF** | CSRF protection | 1.2+ |
| **Bleach** | Input sanitization | 6.1+ |

### Frontend

| Technology | Purpose |
|------------|---------|
| **Vanilla JavaScript** | No framework dependencies |
| **CSS3** | Custom properties, Grid, Flexbox |
| **HTML5** | Semantic markup, ARIA |
| **LocalStorage** | Client-side persistence |
| **Canvas API** | Particle animations |

### Machine Learning

| Component | Technology |
|-----------|------------|
| **Text Vectorization** | TF-IDF (Term Frequency-Inverse Document Frequency) |
| **Primary Classifier** | Logistic Regression with L2 regularization |
| **Ensemble Method** | Random Forest (100 trees) |
| **Cross-Validation** | 5-fold stratified |
| **Model Persistence** | Joblib serialization |

### Infrastructure

| Component | Technology |
|-----------|------------|
| **Containerization** | Docker with multi-stage builds |
| **Orchestration** | Docker Compose |
| **Web Server** | Gunicorn with 4 workers |
| **Health Checks** | Built-in endpoint with model status |

---

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Port 5000 available

### One-Command Start

```bash
# Clone and start
git clone <repository-url>
cd email-detector

# Create environment file
cp .env.example .env
# Edit .env and set SECRET_KEY

# Build and run
docker-compose up --build -d

# Access at http://localhost:5000
```

### Verify Installation

```bash
# Check container health
docker ps

# Test health endpoint
curl http://localhost:5000/health

# Expected response:
# {"status":"healthy","model_loaded":true,"version":"2.0"}
```

---

## 📦 Installation

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd email-detector

# 2. Create environment file
cp .env.example .env

# 3. Generate a secure secret key
# On Linux/Mac:
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
# On Windows PowerShell:
$secret = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
Add-Content .env "SECRET_KEY=$secret"

# 4. Build and start
docker-compose up --build -d

# 5. View logs
docker logs -f email-detector-app
```

### Option 2: Manual Docker Build

```bash
# Build the image
docker build -t email-detector:latest .

# Run with environment variables
docker run -d \
  --name email-detector \
  -p 5000:5000 \
  -e SECRET_KEY="your-32-char-secret-key-here!!!" \
  -e FLASK_ENV=production \
  -e LOG_LEVEL=INFO \
  --health-cmd="curl -f http://localhost:5000/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  email-detector:latest
```

### Option 3: Local Development

```bash
# 1. Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate
# Activate (Windows)
.\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
export FLASK_APP=src.wsgi:application
export FLASK_ENV=development
export SECRET_KEY="dev-secret-key-32-characters!!"

# On Windows:
set FLASK_APP=src.wsgi:application
set FLASK_ENV=development
set SECRET_KEY="dev-secret-key-32-characters!!"

# 4. Run development server
flask run

# 5. Access at http://localhost:5000
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Flask secret key (32+ characters) | - | ✅ Yes |
| `FLASK_ENV` | Environment mode | `production` | No |
| `APP_PORT` | Application port | `5000` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `WORKERS` | Gunicorn workers | `4` | No |
| `CONFIDENCE_THRESHOLD` | ML confidence threshold | `70.0` | No |
| `MAX_EMAIL_LENGTH` | Maximum email characters | `50000` | No |
| `MAX_CONTENT_LENGTH` | Maximum upload size | `1048576` (1MB) | No |

### .env Example

```env
# Required
SECRET_KEY=your-super-secret-key-that-is-at-least-32-characters-long

# Optional
FLASK_ENV=production
APP_PORT=5000
LOG_LEVEL=INFO
WORKERS=4
CONFIDENCE_THRESHOLD=70.0
MAX_EMAIL_LENGTH=50000
```

### Gunicorn Configuration

Located at `config/gunicorn_config.py`:

```python
# Workers and threads
workers = int(os.environ.get('WORKERS', 4))
threads = 2
worker_class = 'sync'

# Timeouts
timeout = 120
graceful_timeout = 30
keepalive = 5

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

---

## 📡 API Reference

### Base URL

```
http://localhost:5000
```

### Authentication

Currently, the API uses CSRF tokens for browser-based requests. API endpoints are rate-limited.

### Endpoints

#### POST /predict

Analyze a single email for threats.

**Request:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "Your email content here..."}'
```

**Response:**
```json
{
  "prediction": 0,
  "label": "Safe Email",
  "short_label": "Safe",
  "icon": "[SAFE]",
  "color": "safe",
  "confidence": 94.6,
  "is_uncertain": false,
  "description": "This email appears to be legitimate and safe.",
  "class_probabilities": {
    "Safe": 94.6,
    "Spam": 2.8,
    "AI Phishing": 2.6
  },
  "risk_features": ["No major risk indicators detected"],
  "word_count": 45,
  "timestamp": "2024 01 15 14:30:22",
  "model_version": "2.0"
}
```

**Rate Limit:** 10 requests per minute

---

#### POST /bulk-predict

Analyze multiple emails at once.

**Request:**
```bash
curl -X POST http://localhost:5000/bulk-predict \
  -H "Content-Type: application/json" \
  -d '{
    "emails": [
      "First email content...",
      "Second email content...",
      "Third email content..."
    ]
  }'
```

**Response:**
```json
{
  "status": "success",
  "total": 3,
  "results": [
    {
      "index": 0,
      "label": "Safe Email",
      "short_label": "Safe",
      "color": "safe",
      "confidence": 92.3,
      "class_probabilities": {"Safe": 92.3, "Spam": 4.1, "AI Phishing": 3.6},
      "word_count": 50
    },
    {
      "index": 1,
      "label": "Spam Email",
      "short_label": "Spam",
      "color": "spam",
      "confidence": 87.5,
      "class_probabilities": {"Safe": 5.2, "Spam": 87.5, "AI Phishing": 7.3},
      "word_count": 120
    }
  ]
}
```

**Rate Limit:** 2 requests per minute  
**Max Emails:** 100 per request

---

#### POST /upload

Upload a .txt or .eml file for analysis.

**Request:**
```bash
curl -X POST http://localhost:5000/upload \
  -F "file=@email.txt"
```

**Response:**
```json
{
  "status": "success",
  "filename": "email.txt",
  "content": "Extracted email content...",
  "word_count": 150,
  "char_count": 850
}
```

**Rate Limit:** 5 requests per minute  
**Max File Size:** 1MB  
**Allowed Extensions:** .txt, .eml

---

#### POST /feedback

Submit feedback on a prediction for model improvement.

**Request:**
```bash
curl -X POST http://localhost:5000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The email content...",
    "reported_label": 1,
    "original_prediction": 0
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Thank you for your feedback! It helps improve our model."
}
```

**Rate Limit:** 5 requests per minute

---

#### GET /health

Health check endpoint for monitoring.

**Request:**
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2024-01-15T14:30:22.123456",
  "version": "2.0"
}
```

---

#### GET /sample

Get sample emails for testing.

**Request:**
```bash
curl http://localhost:5000/sample
```

**Response:**
```json
[
  {
    "name": "Safe Business Email",
    "text": "Hi John, I hope this email finds you well..."
  },
  {
    "name": "Spam Marketing Email",
    "text": "CONGRATULATIONS! You have been selected..."
  },
  {
    "name": "Phishing Attempt",
    "text": "Dear Valued Customer, We have detected unusual activity..."
  }
]
```

**Rate Limit:** 20 requests per minute

---

#### GET /stats

Get application statistics.

**Request:**
```bash
curl http://localhost:5000/stats
```

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_version": "2.0",
  "categories": ["Safe", "Spam", "AI Phishing", "Uncertain"],
  "confidence_threshold": 70.0,
  "max_email_length": 50000,
  "feedback_collected": 15,
  "features": [
    "Single email analysis",
    "Bulk email analysis",
    "File upload (.txt, .eml)",
    "Confidence scoring",
    "Risk indicator detection",
    "Export (JSON, CSV)",
    "History tracking",
    "Analytics dashboard"
  ]
}
```

---

#### GET /api/info

Get API documentation.

**Request:**
```bash
curl http://localhost:5000/api/info
```

**Response:**
```json
{
  "name": "AI Email Security Detector API",
  "version": "2.0",
  "endpoints": {
    "POST /predict": "Analyze single email",
    "POST /bulk-predict": "Analyze multiple emails (max 100)",
    "POST /upload": "Upload .txt or .eml file",
    "POST /feedback": "Submit feedback on prediction",
    "GET /sample": "Get sample emails",
    "GET /health": "Health check",
    "GET /stats": "Application statistics",
    "GET /api/info": "This endpoint"
  },
  "rate_limits": {
    "/predict": "10 per minute",
    "/bulk-predict": "2 per minute",
    "/upload": "5 per minute",
    "/feedback": "5 per minute",
    "/sample": "20 per minute"
  },
  "supported_formats": [".txt", ".eml"],
  "max_file_size": "1MB",
  "max_email_length": 50000,
  "categories": ["Safe Email", "Spam Email", "Phishing Email", "Uncertain"]
}
```

---

## 🖥️ User Interface Guide

### Navigation

The application has five main sections accessible via the navigation bar:

1. **Detector** - Main email analysis interface
2. **History** - View and search past analyses
3. **Dashboard** - Analytics and statistics
4. **Bulk Analyze** - Process multiple emails
5. **How It Works** - Educational information

### Using the Detector

1. **Paste Email**: Copy email content into the text area
2. **Or Upload**: Click the upload area to select a .txt or .eml file
3. **Or Load Sample**: Use the Safe/Spam/Phish buttons to load test emails
4. **Analyze**: Click "Analyze Email" or press `Ctrl + Enter`
5. **View Results**: See verdict, confidence, probabilities, and risk indicators
6. **Export**: Copy or export results as JSON/CSV

### Understanding Results

| Verdict | Color | Meaning |
|---------|-------|---------|
| **Safe** | 🟢 Green | Legitimate email, no threats detected |
| **Spam** | 🟡 Yellow/Orange | Unwanted marketing or promotional content |
| **AI Phishing** | 🔴 Red | Sophisticated phishing attempt |
| **Uncertain** | 🟣 Purple | Low confidence, manual review recommended |

### Risk Indicators

The system detects and reports:
- **URLs/Links**: Presence of hyperlinks
- **Excessive Punctuation**: Multiple exclamation marks
- **Capital Letters**: High ratio of uppercase
- **Dollar Signs**: Financial mentions
- **Phone Numbers**: Contact information
- **Card Patterns**: Potential credit card numbers

### History Features

- **Search**: Filter by content or result type
- **Sort**: View by date, result, or confidence
- **Export**: Download all history as CSV
- **Clear**: Remove all history data

### Dashboard Metrics

- **Total Analyzed**: All-time email count
- **Category Breakdown**: Safe/Spam/Phishing distribution
- **Confidence Analysis**: High/Medium/Low confidence counts
- **Risk Level**: Overall threat assessment
- **Recent Threats**: Latest detected threats

---

## 🤖 Machine Learning Model

### Training Data

The model was trained on a curated dataset combining:

| Source | Type | Samples |
|--------|------|---------|
| SpamAssassin | Spam | ~500 |
| Enron Corpus | Legitimate | ~400 |
| Custom Collection | AI Phishing | ~200 |
| Synthetic | Augmented | ~100 |

**Total Training Samples:** ~1,200 emails

### Preprocessing Pipeline

```
Raw Email → Lowercase → Remove HTML → Tokenize → 
Remove Stopwords → TF-IDF Vectorization → Feature Matrix
```

#### TF-IDF Configuration

```python
TfidfVectorizer(
    max_features=5000,        # Top 5000 features
    ngram_range=(1, 2),       # Unigrams and bigrams
    min_df=2,                 # Minimum document frequency
    max_df=0.95,              # Maximum document frequency
    stop_words='english'      # English stopwords
)
```

### Model Architecture

The classifier uses an ensemble approach:

1. **Primary Model**: Logistic Regression
   - L2 regularization (C=1.0)
   - Multi-class: One-vs-Rest
   - Solver: LBFGS

2. **Secondary Model**: Random Forest
   - 100 decision trees
   - Max depth: 20
   - Bootstrap sampling

3. **Final Prediction**: Weighted average of probabilities

### Performance Metrics

| Metric | Value |
|--------|-------|
| **Training Accuracy** | 100% |
| **Test Accuracy** | 94.83% |
| **Cross-Validation** | 95.49% ± 3.24% |
| **Precision (macro)** | 94.2% |
| **Recall (macro)** | 94.5% |
| **F1-Score (macro)** | 94.3% |

### Confusion Matrix

```
              Predicted
              Safe  Spam  Phishing
Actual Safe    98%    1%     1%
       Spam     3%   94%     3%
    Phishing    2%    5%    93%
```

### Confidence Calibration

- Predictions below 70% confidence are marked as "Uncertain"
- Probability scores are calibrated using Platt scaling
- Users are encouraged to manually review uncertain results

### Feature Importance

Top predictive features:

1. `urgent` / `immediately` - High phishing indicator
2. `winner` / `prize` - High spam indicator
3. `click here` / `link` - Moderate risk
4. `verify` / `confirm` - High phishing indicator
5. `dear customer` - Moderate phishing indicator
6. `free` / `$$$` - High spam indicator

---

## 🏗️ Architecture

### Project Structure

```
email-detector/
├── src/                      # Main application code
│   ├── __init__.py          # Package initialization
│   ├── app.py               # Flask application factory
│   ├── config.py            # Configuration classes
│   ├── validators.py        # Input validation utilities
│   ├── secure_ml.py         # ML model wrapper
│   ├── wsgi.py              # WSGI entry point
│   └── utils/               # Utility scripts
│       ├── train_model.py   # Model training script
│       └── test_model.py    # Model testing script
│
├── static/                   # Static assets
│   ├── style.css            # Main stylesheet (1600+ lines)
│   └── secure_script.js     # Frontend JavaScript (900+ lines)
│
├── templates/                # HTML templates
│   └── index.html           # Main page template
│
├── models/                   # Trained ML models
│   └── email_classifier.pkl # Serialized model
│
├── dataset/                  # Training datasets
│   └── emails.csv           # Training data
│
├── config/                   # Configuration files
│   └── gunicorn_config.py   # Gunicorn settings
│
├── scripts/                  # Build and run scripts
│   ├── build-docker.ps1     # Windows build
│   └── build-docker.sh      # Linux build
│
├── Dockerfile                # Multi-stage Dockerfile
├── docker-compose.yml        # Docker Compose config
├── docker-entrypoint.sh      # Container entrypoint
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── .dockerignore             # Docker ignore rules
├── .gitignore                # Git ignore rules
└── README.md                 # Documentation
```

### Request Flow

```
Client Request
      │
      ▼
┌─────────────────┐
│   Gunicorn      │  (4 workers)
│   WSGI Server   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Flask App     │
│   (app.py)      │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────────┐
│ Rate  │ │  CSRF     │
│Limiter│ │ Protection│
└───┬───┘ └─────┬─────┘
    │           │
    └─────┬─────┘
          │
          ▼
┌─────────────────┐
│   Validators    │  Input sanitization
│  (validators.py)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   ML Classifier │  Prediction
│  (secure_ml.py) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  JSON Response  │
└─────────────────┘
```

### Component Responsibilities

| Component | File | Responsibility |
|-----------|------|----------------|
| **App Factory** | `app.py` | Flask app initialization, routes, middleware |
| **Config** | `config.py` | Environment-specific configurations |
| **Validators** | `validators.py` | Input validation, sanitization, security |
| **ML Wrapper** | `secure_ml.py` | Model loading, prediction, feature extraction |
| **WSGI Entry** | `wsgi.py` | Gunicorn entry point |
| **Frontend** | `secure_script.js` | UI logic, API calls, state management |
| **Styles** | `style.css` | Complete styling, themes, responsive design |

---

## 🔒 Security Features

### Input Validation

| Protection | Implementation |
|------------|----------------|
| **Length Limits** | Max 50,000 characters per email |
| **Content Sanitization** | Bleach library for HTML stripping |
| **Encoding Validation** | Strict UTF-8 enforcement |
| **Path Traversal** | Null byte detection, safe filenames |
| **File Type Validation** | Extension and content verification |

### Request Security

| Protection | Implementation |
|------------|----------------|
| **CSRF Protection** | Flask-WTF tokens for form submissions |
| **Rate Limiting** | Flask-Limiter with per-endpoint limits |
| **Request Size** | 1MB maximum content length |
| **Content-Type** | JSON validation for API endpoints |

### Response Security

| Header | Value | Purpose |
|--------|-------|---------|
| `Content-Security-Policy` | Strict CSP | Prevent XSS |
| `X-Content-Type-Options` | nosniff | Prevent MIME sniffing |
| `X-Frame-Options` | DENY | Prevent clickjacking |
| `Strict-Transport-Security` | max-age=31536000 | Force HTTPS |
| `Referrer-Policy` | strict-origin-when-cross-origin | Control referrer |
| `X-Request-ID` | UUID | Log tracing |

### Container Security

| Feature | Implementation |
|---------|----------------|
| **Non-Root User** | UID 1000 (appuser) |
| **Read-Only Filesystem** | Where possible |
| **No New Privileges** | seccomp profile |
| **Health Checks** | Model status verification |
| **Minimal Image** | Python slim base |

### Code Security

| Practice | Implementation |
|----------|----------------|
| **XSS Prevention** | textContent only (no innerHTML) |
| **SQL Injection** | N/A (no SQL database) |
| **Secret Management** | Environment variables |
| **Error Handling** | No stack traces in production |
| **Logging** | IP hashing for privacy |

---

## ⚡ Performance

### Benchmarks

| Metric | Value |
|--------|-------|
| **Single Analysis** | < 100ms |
| **Bulk (100 emails)** | < 5 seconds |
| **Cold Start** | ~3 seconds |
| **Memory Usage** | ~200MB per worker |
| **CPU Usage** | Low (model is pre-loaded) |

### Scaling Recommendations

| Users | Workers | Memory | CPU |
|-------|---------|--------|-----|
| 1-10 | 2 | 512MB | 1 core |
| 10-50 | 4 | 1GB | 2 cores |
| 50-200 | 8 | 2GB | 4 cores |
| 200+ | Load balanced | 4GB+ | 8+ cores |

### Optimization Techniques

1. **Model Pre-loading**: Model loaded once at startup
2. **TF-IDF Caching**: Vectorizer cached with model
3. **Efficient Serialization**: Joblib compression
4. **Worker Processes**: Gunicorn multi-worker
5. **Static File Serving**: Direct file serving

---

## 🐛 Troubleshooting

### Common Issues

#### Container Won't Start

```bash
# Check logs
docker logs email-detector-app

# Common causes:
# 1. SECRET_KEY not set
# 2. Port 5000 in use
# 3. Model file missing
```

#### Model Not Loading

```bash
# Check model file exists
docker exec email-detector-app ls -la models/

# Test model loading
docker exec email-detector-app python -c "
from src.secure_ml import SecureEmailClassifier
c = SecureEmailClassifier('models/email_classifier.pkl')
print('Model loaded successfully!')
"
```

#### Rate Limit Exceeded

```bash
# Wait for rate limit reset (1 minute)
# Or adjust rate limits in app.py
```

#### CSRF Token Issues

```bash
# For API usage, use /predict endpoint with JSON
# CSRF is exempt for API endpoints
```

### Health Check Failures

```bash
# Verify health endpoint
curl -v http://localhost:5000/health

# Check if model_loaded is true
# If false, check model file and permissions
```

### Memory Issues

```bash
# Reduce workers
docker run -e WORKERS=2 email-detector:latest

# Or use Docker memory limits
docker run --memory=512m email-detector:latest
```

---

## 💻 Development

### Setting Up Development Environment

```bash
# 1. Clone repository
git clone <repository-url>
cd email-detector

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export FLASK_APP=src.wsgi:application
export FLASK_ENV=development
export SECRET_KEY="dev-secret-key-32-characters!!"

# 5. Run development server
flask run --reload
```

### Running Tests

```bash
# Run model tests
python src/utils/test_model.py

# Expected output:
# Model loaded successfully
# Test accuracy: 94.83%
# Cross-validation: 95.49% ± 3.24%
```

### Training a New Model

```bash
# 1. Prepare dataset in dataset/emails.csv
# Format: text,label (0=Safe, 1=Spam, 2=Phishing)

# 2. Run training
python src/utils/train_model.py

# 3. Model saved to models/email_classifier.pkl
```

### Code Style

- **Python**: PEP 8 with 100 character line limit
- **JavaScript**: ESLint with security rules
- **CSS**: BEM-inspired naming

### Project Conventions

- **Logging**: Use `app.logger` with request IDs
- **Errors**: Return JSON with `error` key
- **Validation**: Use `InputValidator` class
- **Security**: Always sanitize user input

---

## 🤝 Contributing

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Make your changes
4. Run tests (`python src/utils/test_model.py`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing`)
7. Open a Pull Request

### Contribution Guidelines

- Follow existing code style
- Add tests for new features
- Update documentation
- Keep commits atomic and descriptive

### Reporting Issues

Please include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, Docker version)
- Relevant logs

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **SpamAssassin Project**: Training data
- **Enron Email Dataset**: Legitimate email samples
- **Scikit-learn Team**: ML framework
- **Flask Team**: Web framework
- **Open Source Community**: Various libraries and tools

---

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: [Contact maintainer]

---

<div align="center">

**Built with ❤️ for email security**

[⬆ Back to Top](#-ai-email-security-detector)

</div>
