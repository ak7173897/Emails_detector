"""
Test if the model can be loaded successfully
"""
import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

print("Testing model loading...")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Check if model file exists
model_path = os.path.join(parent_dir, "models", "email_classifier.pkl")
if os.path.exists(model_path):
    print(f"Model file exists at: {model_path}")
    print(f"  File size: {os.path.getsize(model_path)} bytes")
else:
    print(f"Model file NOT found at: {model_path}")
    sys.exit(1)

# Try to load the model
try:
    from src.secure_ml import SecureEmailClassifier
    print("Imported SecureEmailClassifier")
    
    classifier = SecureEmailClassifier(model_path)
    print("Created classifier instance")
    
    if classifier.pipeline is not None:
        print("Model loaded successfully!")
        
        # Try a test prediction
        test_email = "Hello, this is a test email"
        result = classifier.predict_secure(test_email)
        print(f"Test prediction works: {result}")
        
        print("\n=== SUCCESS ===")
        print("Model can be loaded and used")
        sys.exit(0)
    else:
        print("Model loaded but pipeline is None")
        sys.exit(1)
        
except Exception as e:
    print(f"Error loading model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
