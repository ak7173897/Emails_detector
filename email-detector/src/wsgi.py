"""
Production WSGI Configuration for Email Security Detector
Single-container optimized setup
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

try:
    # Add the project directory to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(project_root)
    sys.path.insert(0, parent_dir)
    
    # Set production environment
    os.environ.setdefault('FLASK_ENV', 'production')
    
    logger.info("Starting Email Security Detector (Single Container)...")
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Project root: {project_root}")
    
    # Import the Flask application
    from src.app import create_app
    
    # Create the application instance
    logger.info("Creating Flask app...")
    application = create_app('production')
    logger.info("Flask app created successfully")
    
except Exception as e:
    logger.error(f"Failed to create application: {e}", exc_info=True)
    raise

if __name__ == "__main__":
    # This should not be used in production
    application.run(debug=False, host='0.0.0.0', port=5000)
