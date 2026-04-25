"""
=============================================================================
AI Email Security Detector - Production-Ready Secure Flask Backend
=============================================================================
SECURITY FEATURES:
- Input validation and sanitization
- CSRF protection
- Rate limiting (in-memory)
- Security headers
- Secure file handling
- Proper error handling
- Logging and monitoring with request IDs
=============================================================================
"""

from flask import Flask, request, jsonify, render_template, abort, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect, generate_csrf
from whitenoise import WhiteNoise
import os
import json
import logging
import logging.handlers
import hashlib
import uuid
from datetime import datetime, timedelta
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename
import bleach

# Import our secure modules
from .config import config
from .validators import InputValidator, ValidationError
from .secure_ml import SecureEmailClassifier

# Initialize Flask app
def create_app(config_name=None):
    """Application factory pattern for secure Flask app."""
    
    # Resolve project root (parent of backend/)
    import pathlib
    project_root = pathlib.Path(__file__).resolve().parent.parent
    
    app = Flask(
        __name__,
        template_folder=str(project_root / 'templates'),
        static_folder=str(project_root / 'static')
    )
    
    # Initialize WhiteNoise for production static file serving
    app.wsgi_app = WhiteNoise(app.wsgi_app, root=str(project_root / 'static'), prefix='static/')
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'production')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    csrf = CSRFProtect(app)
    
    # Security headers with Talisman
    csp = {
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        'img-src': ["'self'", "data:", "https:"],
        'font-src': ["'self'", "https://fonts.gstatic.com", "data:"],
        'connect-src': "'self'",
        'frame-ancestors': "'none'"
    }
    
    # Enable Talisman security headers (disabled force_https for local dev)
    Talisman(app, 
        force_https=False,  # Set to True in production behind HTTPS proxy
        strict_transport_security=not app.debug,
        strict_transport_security_max_age=31536000,
        content_security_policy=csp,
        referrer_policy='strict-origin-when-cross-origin',
        session_cookie_secure=not app.debug,
        session_cookie_http_only=True
    )
    
    # Rate limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://'),
        default_limits=["100 per day", "30 per hour"]
    )
    
    # Configure logging for production (use stdout/stderr for Docker)
    if not app.debug:
        # Stream handler for Docker logs
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info("Application logging configured for production")
    
    # Initialize ML model
    model_path = app.config.get('MODEL_PATH', 'models/email_classifier.pkl')
    try:
        classifier = SecureEmailClassifier(model_path)
        app.classifier = classifier
        app.logger.info(f"ML model loaded successfully from {model_path}")
    except Exception as e:
        app.logger.error(f"CRITICAL: Failed to load ML model: {str(e)}")
        app.classifier = None
        # In production, fail fast if model cannot be loaded
        if not app.debug:
            app.logger.critical("Cannot start without ML model in production mode!")
            # Allow container to start but mark as unhealthy
    
    # Request ID middleware for log tracing
    @app.before_request
    def add_request_id():
        """Add unique request ID for log tracing."""
        g.request_id = str(uuid.uuid4())[:8]
    
    @app.after_request
    def add_request_id_header(response):
        """Add request ID to response headers for debugging."""
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        return response
    
    # Error handlers
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        """Handle validation errors securely."""
        req_id = getattr(g, 'request_id', 'unknown')
        app.logger.warning(f"[{req_id}] Validation error from {request.remote_addr}: {str(e)}")
        return jsonify({'error': str(e), 'request_id': req_id}), 400
    
    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_file(e):
        """Handle file size exceeded."""
        return jsonify({'error': 'File too large. Maximum size is 1MB.'}), 413
    
    @app.errorhandler(429)
    def handle_rate_limit(e):
        """Handle rate limiting."""
        req_id = getattr(g, 'request_id', 'unknown')
        app.logger.warning(f"[{req_id}] Rate limit exceeded for {request.remote_addr}")
        return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        """Handle internal errors without exposing details."""
        req_id = getattr(g, 'request_id', 'unknown')
        app.logger.error(f"[{req_id}] Internal error: {str(e)}")
        return jsonify({'error': 'Internal server error occurred.', 'request_id': req_id}), 500
    
    # Security utilities
    def get_client_ip():
        """Get client IP address securely."""
        if request.environ.get('HTTP_X_FORWARDED_FOR'):
            return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        return request.environ.get('REMOTE_ADDR', 'unknown')
    
    def hash_ip(ip_address):
        """Hash IP address for privacy-compliant logging with salt."""
        salt = app.config.get('SECRET_KEY', 'default-salt')[:16]
        salted = f"{salt}{ip_address}".encode()
        return hashlib.sha256(salted).hexdigest()[:16]
    
    # Routes
    @app.route('/')
    def index():
        """Serve the main HTML page."""
        return render_template('index.html', csrf_token=generate_csrf())
    
    @app.route('/predict', methods=['POST'])
    @csrf.exempt  # Exempt from CSRF for API usage - input is validated below
    @limiter.limit("100 per minute")
    def predict():
        """
        Secure email prediction endpoint.
        Rate limited and fully validated.
        """
        client_ip = get_client_ip()
        hashed_ip = hash_ip(client_ip)
        
        # Check if model is loaded
        if not app.classifier:
            app.logger.error(f"Prediction attempted but model not loaded - IP: {hashed_ip}")
            return jsonify({
                'error': 'Service temporarily unavailable. Please try again later.'
            }), 503
        
        # Validate content type
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        try:
            # Parse and validate JSON
            data = request.get_json(force=True)
            validated_data = InputValidator.validate_json_request(data)
            
            # Extract email text
            email_text = validated_data.get('text', '').strip()
            
            if not email_text:
                raise ValidationError("Email text is required")
            
            # Validate email content
            email_validation = InputValidator.validate_email_content(email_text)
            sanitized_content = email_validation['content']
            
            # Make secure prediction
            prediction_result = app.classifier.predict_secure(sanitized_content)
            
            # Map prediction to labels
            label_mapping = {
                0: {
                    "name": "Safe Email",
                    "short": "Safe", 
                    "icon": "[SAFE]",
                    "color": "safe",
                    "description": "This email appears to be legitimate and safe."
                },
                1: {
                    "name": "Spam Email",
                    "short": "Spam",
                    "icon": "[SPAM]", 
                    "color": "spam",
                    "description": "This email shows characteristics of spam or unwanted marketing."
                },
                2: {
                    "name": "Phishing Email",
                    "short": "AI Phishing",
                    "icon": "[DANGER]",
                    "color": "phishing", 
                    "description": "This email appears to be a phishing attempt designed to steal credentials or personal information."
                }
            }
            
            prediction = prediction_result['prediction']
            confidence = prediction_result['confidence']
            is_uncertain = prediction_result['is_uncertain']
            
            # Get label info
            label_info = label_mapping.get(prediction, label_mapping[0]).copy()
            
            # Handle uncertain predictions
            if is_uncertain:
                label_info = {
                    "name": "Uncertain Classification",
                    "short": "Uncertain",
                    "icon": "[?]",
                    "color": "uncertain",
                    "description": f"The model confidence is only {confidence:.1f}%. Manual review is recommended for this email."
                }
            
            # Build class probabilities  
            class_probs = {}
            for i, prob in enumerate(prediction_result['probabilities']):
                class_name = label_mapping[i]['short']
                class_probs[class_name] = round(prob * 100, 1)
            
            # Extract risk features (simplified and secure)
            risk_features = []
            features = prediction_result['features']
            
            if features.get('has_url', 0):
                risk_features.append("Contains URLs or links")
            if features.get('exclamation_count', 0) > 3:
                risk_features.append(f"Excessive exclamation marks ({features['exclamation_count']})")
            if features.get('caps_ratio', 0) > 0.3:
                risk_features.append("High proportion of capital letters")
            if features.get('dollar_count', 0) > 2:
                risk_features.append("Multiple dollar sign mentions")
            if features.get('has_phone', 0):
                risk_features.append("Contains phone number")
            if features.get('has_card', 0):
                risk_features.append("Contains potential credit card number")
            
            if not risk_features:
                risk_features = ["No major risk indicators detected"]
            
            # Build response
            response_data = {
                'prediction': prediction,
                'label': label_info['name'],
                'short_label': label_info['short'],
                'icon': label_info['icon'],
                'color': label_info['color'],
                'confidence': round(confidence, 1),
                'is_uncertain': is_uncertain,
                'description': label_info['description'],
                'class_probabilities': class_probs,
                'risk_features': risk_features,
                'word_count': email_validation['word_count'],
                'timestamp': datetime.now().strftime("%Y %m %d %H:%M:%S"),
                'model_version': prediction_result.get('model_version', 'unknown')
            }
            
            # Log prediction (privacy-compliant)
            app.logger.info(
                f"Prediction: {label_info['short']}, "
                f"Confidence: {confidence:.1f}%, "
                f"Words: {email_validation['word_count']}, "
                f"IP: {hashed_ip}"
            )
            
            return jsonify(response_data)
            
        except ValidationError as e:
            raise e
        except Exception as e:
            app.logger.error(f"Prediction error for IP {hashed_ip}: {str(e)}")
            return jsonify({'error': 'Prediction failed. Please try again.'}), 500
    
    @app.route('/feedback', methods=['POST'])
    @limiter.limit("5 per minute")
    @csrf.exempt  # Exempt from CSRF for API usage, but validate in other ways
    def feedback():
        """
        Secure feedback endpoint for model improvement.
        """
        client_ip = get_client_ip()
        hashed_ip = hash_ip(client_ip)
        
        try:
            # Validate JSON request
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json(force=True)
            validated_data = InputValidator.validate_json_request(data)
            
            # Required fields
            email_text = validated_data.get('text', '')
            reported_label = validated_data.get('reported_label')
            original_prediction = validated_data.get('original_prediction')
            
            if not email_text or reported_label is None:
                raise ValidationError("Missing required fields: text and reported_label")
            
            # Create secure feedback entry
            feedback_entry = {
                'timestamp': datetime.now().isoformat(),
                'email_preview': email_text[:100] + '...' if len(email_text) > 100 else email_text,
                'reported_label': reported_label,
                'original_prediction': original_prediction,
                'ip_hash': hashed_ip,
                'word_count': len(email_text.split())
            }
            
            # Save feedback securely
            feedback_dir = 'feedback'
            os.makedirs(feedback_dir, exist_ok=True)
            
            # Use date-based filename for better organization
            date_str = datetime.now().strftime("%Y%m%d")
            feedback_file = os.path.join(feedback_dir, f'feedback_{date_str}.json')
            
            # Append to daily feedback file
            feedbacks = []
            if os.path.exists(feedback_file):
                try:
                    with open(feedback_file, 'r', encoding='utf-8') as f:
                        feedbacks = json.load(f)
                except (json.JSONDecodeError, IOError):
                    feedbacks = []
            
            feedbacks.append(feedback_entry)
            
            # Save with proper error handling
            try:
                with open(feedback_file, 'w', encoding='utf-8') as f:
                    json.dump(feedbacks, f, indent=2, ensure_ascii=False)
            except IOError as e:
                app.logger.error(f"Failed to save feedback: {str(e)}")
                return jsonify({'error': 'Failed to save feedback'}), 500
            
            # Log feedback received
            app.logger.info(
                f"Feedback received - Original: {original_prediction}, "
                f"Reported: {reported_label}, IP: {hashed_ip}"
            )
            
            return jsonify({
                'status': 'success', 
                'message': 'Thank you for your feedback! It helps improve our model.'
            })
            
        except ValidationError as e:
            raise e
        except Exception as e:
            app.logger.error(f"Feedback error for IP {hashed_ip}: {str(e)}")
            return jsonify({'error': 'Failed to process feedback'}), 500
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring."""
        model_status = app.classifier is not None
        
        health_data = {
            'status': 'healthy' if model_status else 'degraded',
            'model_loaded': model_status,
            'timestamp': datetime.now().isoformat(),
            'version': '2.0'
        }
        
        # Return 200 even if model not loaded - app is still responsive
        return jsonify(health_data), 200
    
    @app.route('/sample', methods=['GET'])
    @limiter.limit("20 per minute")
    def get_samples():
        """Return sample emails for testing (rate limited)."""
        samples = [
            {
                "name": "Safe Business Email",
                "text": "Hi John, I hope this email finds you well. I wanted to follow up on our meeting last week regarding the Q3 budget planning. Could we schedule a call this week to discuss the revised numbers? Let me know what works best for you. Best regards, Sarah Johnson, Project Manager"
            },
            {
                "name": "Spam Marketing Email", 
                "text": "CONGRATULATIONS! You have been selected as our LUCKY WINNER! Claim your prize of $1,000,000 NOW! This is a LIMITED TIME OFFER! Click here immediately to claim before it expires! Make money fast working from home! No experience needed!"
            },
            {
                "name": "Phishing Attempt",
                "text": "Dear Valued Customer, We have detected unusual activity on your account from an unrecognized device. As a security measure, please verify your identity immediately by clicking the link below and entering your credentials. Failure to complete verification within 24 hours will result in permanent account suspension."
            }
        ]
        
        return jsonify(samples)
    
    @app.route('/upload', methods=['POST'])
    @limiter.limit("5 per minute")
    def upload_file():
        """Secure file upload endpoint with content validation."""
        try:
            # Check if file is present
            if 'file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400
            
            file = request.files['file']
            
            # Validate file metadata
            file_info = InputValidator.validate_file_upload(
                file, app.config['ALLOWED_EXTENSIONS']
            )
            
            # Read file content with strict encoding
            try:
                raw_content = file.read()
                
                # Check for binary content (non-text files)
                if b'\x00' in raw_content[:1000]:  # Check first 1KB for null bytes
                    raise ValidationError("Binary file content not allowed")
                
                # Strict UTF-8 decoding - reject malformed content
                content = raw_content.decode('utf-8')
                
            except UnicodeDecodeError:
                raise ValidationError("File must be valid UTF-8 text")
            
            # Check for suspicious patterns
            suspicious_patterns = ['<script', '<?php', '<%', 'javascript:', 'vbscript:']
            content_lower = content.lower()
            for pattern in suspicious_patterns:
                if pattern in content_lower:
                    app.logger.warning(f"Suspicious pattern detected in upload: {pattern}")
                    raise ValidationError("File contains potentially malicious content")
            
            # Validate as email content
            email_validation = InputValidator.validate_email_content(content)
            
            return jsonify({
                'status': 'success',
                'filename': file_info['safe_filename'],
                'content': email_validation['content'],
                'word_count': email_validation['word_count'],
                'char_count': email_validation['char_count']
            })
            
        except ValidationError as e:
            raise e
        except Exception as e:
            app.logger.error(f"File upload error: {str(e)}")
            return jsonify({'error': 'File upload failed'}), 500

    csrf.exempt(app.view_functions['upload_file'])
    
    @app.route('/bulk-predict', methods=['POST'])
    @csrf.exempt
    @limiter.limit("2 per minute")
    def bulk_predict():
        """
        Bulk email prediction endpoint.
        Accepts array of emails and returns array of predictions.
        Rate limited more strictly due to higher resource usage.
        """
        client_ip = get_client_ip()
        hashed_ip = hash_ip(client_ip)
        
        # Check if model is loaded
        if not app.classifier:
            return jsonify({'error': 'Service temporarily unavailable'}), 503
        
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        try:
            data = request.get_json(force=True)
            emails = data.get('emails', [])
            
            if not isinstance(emails, list):
                raise ValidationError("emails must be an array")
            
            if len(emails) > 100:
                raise ValidationError("Maximum 100 emails per batch")
            
            if len(emails) == 0:
                raise ValidationError("No emails provided")
            
            results = []
            label_mapping = {
                0: {"name": "Safe Email", "short": "Safe", "color": "safe"},
                1: {"name": "Spam Email", "short": "Spam", "color": "spam"},
                2: {"name": "Phishing Email", "short": "AI Phishing", "color": "phishing"}
            }
            
            for i, email_text in enumerate(emails):
                try:
                    if not email_text or len(email_text.strip()) < 10:
                        results.append({
                            'index': i,
                            'error': 'Email too short (minimum 10 characters)'
                        })
                        continue
                    
                    # Validate and sanitize
                    email_validation = InputValidator.validate_email_content(email_text)
                    sanitized_content = email_validation['content']
                    
                    # Make prediction
                    prediction_result = app.classifier.predict_secure(sanitized_content)
                    
                    prediction = prediction_result['prediction']
                    confidence = prediction_result['confidence']
                    is_uncertain = prediction_result['is_uncertain']
                    
                    label_info = label_mapping.get(prediction, label_mapping[0])
                    
                    if is_uncertain:
                        label_info = {
                            "name": "Uncertain",
                            "short": "Uncertain",
                            "color": "uncertain"
                        }
                    
                    class_probs = {}
                    for j, prob in enumerate(prediction_result['probabilities']):
                        class_name = label_mapping[j]['short']
                        class_probs[class_name] = round(prob * 100, 1)
                    
                    results.append({
                        'index': i,
                        'label': label_info['name'],
                        'short_label': label_info['short'],
                        'color': label_info['color'],
                        'confidence': round(confidence, 1),
                        'class_probabilities': class_probs,
                        'word_count': email_validation['word_count']
                    })
                    
                except Exception as e:
                    results.append({
                        'index': i,
                        'error': str(e)
                    })
            
            app.logger.info(f"Bulk prediction: {len(emails)} emails, IP: {hashed_ip}")
            
            return jsonify({
                'status': 'success',
                'total': len(emails),
                'results': results
            })
            
        except ValidationError as e:
            raise e
        except Exception as e:
            app.logger.error(f"Bulk prediction error: {str(e)}")
            return jsonify({'error': 'Bulk prediction failed'}), 500
    
    @app.route('/stats', methods=['GET'])
    @limiter.limit("30 per minute")
    def get_stats():
        """
        Get application statistics and metrics.
        """
        try:
            # Get feedback stats if available
            feedback_dir = 'feedback'
            feedback_count = 0
            if os.path.exists(feedback_dir):
                for filename in os.listdir(feedback_dir):
                    if filename.endswith('.json'):
                        try:
                            with open(os.path.join(feedback_dir, filename), 'r') as f:
                                feedbacks = json.load(f)
                                feedback_count += len(feedbacks)
                        except (json.JSONDecodeError, IOError):
                            pass
            
            return jsonify({
                'status': 'ok',
                'model_loaded': app.classifier is not None,
                'model_version': '2.0',
                'categories': ['Safe', 'Spam', 'AI Phishing', 'Uncertain'],
                'confidence_threshold': app.config.get('CONFIDENCE_THRESHOLD', 70.0),
                'max_email_length': app.config.get('MAX_EMAIL_LENGTH', 50000),
                'feedback_collected': feedback_count,
                'features': [
                    'Single email analysis',
                    'Bulk email analysis',
                    'File upload (.txt, .eml)',
                    'Confidence scoring',
                    'Risk indicator detection',
                    'Export (JSON, CSV)',
                    'History tracking',
                    'Analytics dashboard'
                ]
            })
            
        except Exception as e:
            app.logger.error(f"Stats error: {str(e)}")
            return jsonify({'error': 'Failed to get stats'}), 500
    
    @app.route('/api/info', methods=['GET'])
    def api_info():
        """API information endpoint."""
        return jsonify({
            'name': 'AI Email Security Detector API',
            'version': '2.0',
            'endpoints': {
                'POST /predict': 'Analyze single email',
                'POST /bulk-predict': 'Analyze multiple emails (max 100)',
                'POST /upload': 'Upload .txt or .eml file',
                'POST /feedback': 'Submit feedback on prediction',
                'GET /sample': 'Get sample emails',
                'GET /health': 'Health check',
                'GET /stats': 'Application statistics',
                'GET /api/info': 'This endpoint'
            },
            'rate_limits': {
                '/predict': '10 per minute',
                '/bulk-predict': '2 per minute',
                '/upload': '5 per minute',
                '/feedback': '5 per minute',
                '/sample': '20 per minute'
            },
            'supported_formats': ['.txt', '.eml'],
            'max_file_size': '1MB',
            'max_email_length': 50000,
            'categories': ['Safe Email', 'Spam Email', 'Phishing Email', 'Uncertain']
        })
    
    return app


if __name__ == '__main__':
    # Only for development - use WSGI server in production
    import logging
    logging.basicConfig(level=logging.INFO)
    
    app = create_app('development')
    
    print("\n" + "=" * 60)
    print("  AI Email Security Detector - Development Mode")
    print("  WARNING: This is not suitable for production!")
    print("  Use a proper WSGI server like Gunicorn for production.")
    print("=" * 60 + "\n")
    
    app.run(
        debug=False,
        host='127.0.0.1',
        port=5000,
        threaded=True
    )
