# Project Report: AI Email Security Detector

## 1. Executive Summary

The AI Email Security Detector is a Flask-based web application that classifies email content into security-related categories such as Safe, Spam, Phishing, and Uncertain. The project combines a trained scikit-learn model with a browser-based interface, JSON API endpoints, file upload support, feedback capture, and containerized deployment.

The codebase is structured like a production-minded application rather than a classroom prototype. It includes secure request handling, rate limiting, CSRF controls, content sanitization, security headers, model persistence, Docker support, and health endpoints. At the same time, a few maintenance issues remain, especially around documentation accuracy, test reliability, and model artifact metadata.

## 2. Project Objectives

- Detect malicious or suspicious emails using machine learning.
- Provide a simple web UI for single-email analysis.
- Support bulk analysis and file-based email ingestion.
- Expose backend APIs for programmatic access.
- Apply security best practices appropriate for a public-facing Flask service.
- Package the application for local and Docker-based deployment.

## 3. Scope and Core Functionality

The current implementation provides:

- Single-email classification through `POST /predict`
- Bulk classification through `POST /bulk-predict`
- File upload support for `.txt` and `.eml`
- Feedback collection through `POST /feedback`
- Sample email retrieval through `GET /sample`
- Operational monitoring through `GET /health`, `GET /stats`, and `GET /api/info`
- Frontend assets in `templates/index.html`, `static/style.css`, and `static/secure_script.js`

The classifier is loaded from `models/email_classifier.pkl`, and the backend is initialized in [src/app.py](C:\Users\DELL\Desktop\email-detector-ankita\email-detector\src\app.py) with a WSGI entrypoint in [src/wsgi.py](C:\Users\DELL\Desktop\email-detector-ankita\email-detector\src\wsgi.py).

## 4. Architecture Overview

### Backend

- Framework: Flask
- Application style: app factory pattern via `create_app`
- WSGI serving: Gunicorn-oriented entrypoint
- Static asset serving: WhiteNoise
- Security middleware: Flask-Talisman, Flask-WTF CSRF, Flask-Limiter

### Machine Learning Layer

- Wrapper class: `SecureEmailClassifier`
- Location: [src/secure_ml.py](C:\Users\DELL\Desktop\email-detector-ankita\email-detector\src\secure_ml.py)
- Model format: Joblib-serialized scikit-learn pipeline
- Inference output: prediction label, confidence, class probabilities, and extracted risk indicators

### Validation Layer

- Central validator: `InputValidator`
- Location: [src/validators.py](C:\Users\DELL\Desktop\email-detector-ankita\email-detector\src\validators.py)
- Responsibilities:
  - input sanitization with Bleach
  - length checks
  - JSON payload validation
  - upload filename and extension validation
  - file content safety checks

### Frontend

- Server-rendered HTML template
- Vanilla JavaScript for API interaction and UI behavior
- Custom CSS for responsive styling and theme behavior

## 5. Technology Stack

### Languages and Frameworks

- Python 3.11+ target in docs, running locally here on Python 3.13
- Flask for web serving
- HTML, CSS, JavaScript for the frontend

### Security and Middleware

- `flask-talisman`
- `flask-wtf`
- `flask-limiter`
- `bleach`
- `whitenoise`

### Machine Learning and Data

- `scikit-learn`
- `pandas`
- `numpy`
- `joblib`

### Deployment

- Docker
- Docker Compose
- Gunicorn

## 6. Functional Workflow

The primary request flow is:

1. Client sends email text or file content.
2. Flask route validates request type and payload.
3. `InputValidator` sanitizes and constrains the content.
4. `SecureEmailClassifier` preprocesses text and runs model inference.
5. Backend maps prediction to UI/API labels and returns JSON.
6. Frontend renders the verdict, confidence, and risk cues.

Additional workflows include:

- Feedback persistence into date-based JSON files under `feedback/`
- File upload parsing with UTF-8 enforcement and suspicious-pattern rejection
- Health and stats reporting for operations visibility

## 7. Security Design

This project shows strong emphasis on secure-by-default behavior:

- CSRF protection is enabled for the app, with selective exemptions for API-style JSON endpoints.
- Rate limiting is configured globally and per route.
- Talisman applies CSP, referrer policy, and session cookie protections.
- User input is sanitized before classification.
- Uploads are limited by extension, filename safety, file size, UTF-8 decoding, and content scanning.
- IPs are hashed before logging for better privacy handling.
- Responses include request IDs for traceability.

This is one of the stronger parts of the codebase and is appropriate for a security-focused application.

## 8. Model Design Summary

Based on [src/secure_ml.py](C:\Users\DELL\Desktop\email-detector-ankita\email-detector\src\secure_ml.py), the intended training design includes:

- TF-IDF text vectorization
- Ensemble classification using Logistic Regression and Random Forest
- Probability calibration with `CalibratedClassifierCV`
- Confidence-based uncertainty handling
- Additional heuristic feature extraction for explainability

The inference wrapper also derives risk indicators such as:

- URL presence
- excessive punctuation
- capitalization ratio
- dollar-sign frequency
- phone-number presence
- card-number-like patterns

## 9. Deployment and Operations

The repository includes:

- [Dockerfile](C:\Users\DELL\Desktop\email-detector-ankita\email-detector\Dockerfile)
- [docker-compose.yml](C:\Users\DELL\Desktop\email-detector-ankita\email-detector\docker-compose.yml)
- local run scripts for Windows
- shell and PowerShell scripts for Docker build/run helpers

Operational features present in the code:

- health endpoint
- configurable worker count
- environment-driven configuration
- logging to stdout and rotating files
- tmpfs mounts for uploads, logs, and feedback in Docker
- non-root and no-new-privileges hardening in Compose

## 10. Verification Performed

The following checks were performed directly against the current workspace:

- Repository structure and major source files were reviewed.
- The serialized model file at `models/email_classifier.pkl` exists.
- A direct Python smoke test successfully loaded the classifier and executed inference.
- The included utility test script failed because it looks for the model in the wrong directory.

### Smoke Test Result

Direct load result:

- `pipeline_loaded = True`
- sample inference returned a valid prediction payload

### Verification Limitation

The included script [src/utils/test_model.py](C:\Users\DELL\Desktop\email-detector-ankita\email-detector\src\utils\test_model.py) currently searches for the model at `src/models/email_classifier.pkl`, while the actual model is stored at `models/email_classifier.pkl`. Because of that path mismatch, the script fails even though the model artifact is present and loadable.

## 11. Strengths

- Good separation between app setup, validation, and ML logic
- Strong attention to input safety and HTTP security controls
- Useful API surface for both UI and programmatic use
- Deployment-ready structure with Docker and WSGI support
- Clear environment-based configuration approach
- Feedback capture and operational endpoints are already in place

## 12. Observed Gaps and Risks

### 1. Test utility path bug

The existing model smoke test is broken because of an incorrect model path assumption. This weakens confidence in local validation and onboarding.

### 2. Missing model metadata artifact

The application looks for a companion metadata JSON file alongside the model. In the current workspace, only `email_classifier.pkl` exists in `models/`, so inference reports `model_version` as `unknown`.

### 3. Documentation and implementation drift

The README describes behavior that does not fully match the current code. One clear example is rate limiting:

- README says `POST /predict` is limited to `10 per minute`
- actual code in [src/app.py](C:\Users\DELL\Desktop\email-detector-ankita\email-detector\src\app.py) uses `100 per minute`

This kind of drift can mislead users, testers, and deployers.

### 4. Some dependencies/config appear unused

The configuration includes SQLAlchemy-related settings and the requirements file includes packages such as `flask-sqlalchemy`, `redis`, `prometheus-flask-exporter`, and `structlog`, but the reviewed application code does not currently use them. This may increase maintenance burden and deployment size.

### 5. Training claims are not fully evidenced by the checked artifacts

The README contains detailed performance claims and dataset source summaries, but the currently present repository artifacts do not include a metadata file or automated report proving the exact shipped model metrics. The training script documents the intended process, but artifact traceability could be stronger.

## 13. Recommendations

### High Priority

- Fix [src/utils/test_model.py](C:\Users\DELL\Desktop\email-detector-ankita\email-detector\src\utils\test_model.py) to point to the correct model path.
- Generate and commit the model metadata JSON file if it is part of the intended release flow.
- Reconcile README endpoint limits and feature claims with the actual implementation.

### Medium Priority

- Add automated tests for Flask endpoints and validator behavior.
- Add a repeatable model evaluation report as part of training output.
- Remove unused dependencies or wire them into the app if they are planned.

### Low Priority

- Add a proper project license file if MIT licensing is intended.
- Separate runtime logs from repository-tracked files if not already ignored.
- Consider moving feedback persistence to a managed store if multi-instance deployment is expected.

## 14. Conclusion

This project is a solid applied machine-learning web application with stronger-than-average security practices for a student or portfolio-style Flask project. Its architecture is understandable, its deployment story is practical, and its feature set is broad enough for demonstration and extension.

The main improvements needed are not architectural rewrites. They are consistency and maintenance fixes: align docs with code, repair the broken local test script, preserve model metadata, and add stronger verification around the shipped artifact. With those addressed, the project would present much more cleanly as a production-oriented email threat detection system.
