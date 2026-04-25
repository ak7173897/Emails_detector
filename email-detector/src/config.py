"""
Production Configuration Management
Secure configuration with environment variables and validation
"""
import os
from datetime import timedelta
from pathlib import Path


class Config:
    """Base configuration class with security defaults."""
    
    # Security Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    
    # Flask Settings  
    DEBUG = False
    TESTING = False
    
    # Rate Limiting (in-memory for single container)
    RATELIMIT_STORAGE_URL = 'memory://'
    RATELIMIT_DEFAULT = "30/minute"
    RATELIMIT_HEADERS_ENABLED = True
    
    # ML Model Settings
    MODEL_PATH = os.environ.get('MODEL_PATH', 'models/email_classifier.pkl')
    CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', '70.0'))
    MAX_EMAIL_LENGTH = int(os.environ.get('MAX_EMAIL_LENGTH', '50000'))
    MIN_EMAIL_LENGTH = int(os.environ.get('MIN_EMAIL_LENGTH', '10'))
    
    # File Upload Settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', '1048576'))  # 1MB
    ALLOWED_EXTENSIONS = {'txt', 'eml'}
    
    # Database Settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///email_detector.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Headers
    CSP_DEFAULT_SRC = "'self'"
    CSP_SCRIPT_SRC = "'self' 'unsafe-inline'"
    CSP_STYLE_SRC = "'self' 'unsafe-inline'"
    CSP_IMG_SRC = "'self' data:"
    
    # Session Settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'app.log')
    
    # Admin Settings
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    
    @staticmethod
    def init_app(app):
        """Initialize application with config."""
        # Create necessary directories (ignore errors in Docker/read-only)
        for folder in [Config.UPLOAD_FOLDER, 'logs', 'models', 'feedback']:
            try:
                os.makedirs(folder, exist_ok=True)
            except OSError:
                pass  # Ignore if can't create (tmpfs will handle in Docker)


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration with enhanced security."""
    DEBUG = False
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_SSL_STRICT = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production-specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            file_handler = RotatingFileHandler(
                cls.LOG_FILE, maxBytes=10240000, backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Email Detector startup')


class DockerConfig(ProductionConfig):
    """Docker-specific configuration"""
    
    # Docker-optimized paths
    UPLOAD_FOLDER = '/app/uploads'
    MODEL_PATH = '/app/models/email_classifier.pkl'
    LOG_FILE = '/app/logs/email_detector.log'
    
    # In-memory rate limiting (no Redis needed)
    RATELIMIT_STORAGE_URL = 'memory://'
    
    # Health check configuration
    HEALTH_CHECK_ENABLED = True
    
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        
        # Docker-specific logging to stdout for container logs
        import logging
        import sys
        
        # Add stdout handler for Docker logs
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s'
        ))
        stdout_handler.setLevel(logging.INFO)
        app.logger.addHandler(stdout_handler)


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'testing': TestingConfig,
    'default': ProductionConfig
}


def get_config(config_name=None):
    """Get configuration class based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')
    
    # Special handling for Docker environment
    if os.path.exists('/app') and config_name == 'production':
        config_name = 'docker'
    
    return config.get(config_name, config['default'])