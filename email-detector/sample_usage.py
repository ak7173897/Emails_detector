"""
=============================================================================
AI Email Security Detector — Standalone Sample Usage
=============================================================================
Demonstrates email classification directly using the pre-trained ML model.
No running server required.

Run:
    python sample_usage.py               # from the email-detector/ directory
    make sample                          # via Makefile
=============================================================================
"""

import os
import sys

# Ensure we can import the src package regardless of working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from src.secure_ml import SecureEmailClassifier  # noqa: E402

# ---------------------------------------------------------------------------
# Sample emails to classify
# ---------------------------------------------------------------------------
SAMPLES = [
    {
        "label": "Legitimate email",
        "text": (
            "Hi Sarah, just a reminder that our weekly team meeting is on Thursday at 2 PM. "
            "Please review the attached agenda and let me know if you have any items to add. "
            "Thanks, John"
        ),
    },
    {
        "label": "Spam / prize scam",
        "text": (
            "CONGRATULATIONS! You have been selected as the WINNER of our $1,000,000 lottery! "
            "ACT NOW — this offer expires in 24 hours! Click here immediately to claim your prize. "
            "Send your bank details to collect your winnings. URGENT RESPONSE REQUIRED!!!"
        ),
    },
    {
        "label": "Phishing / credential theft",
        "text": (
            "Dear valued customer, we have detected suspicious activity on your account. "
            "Your account will be suspended unless you verify your identity within 48 hours. "
            "Please click the link below and enter your username, password, and credit card number "
            "to confirm your identity: http://secure-bank-verify.xyz/login"
        ),
    },
    {
        "label": "AI-generated phishing",
        "text": (
            "I hope this message finds you well. I am writing on behalf of the IT security department "
            "regarding an urgent security update that requires your immediate attention. "
            "We have identified a critical vulnerability in your account that must be patched today. "
            "Please provide your current credentials so we can apply the necessary security patch "
            "and protect your personal information from unauthorized access."
        ),
    },
]

# Label map (matches training labels in train_model.py)
LABEL_MAP = {0: "Safe", 1: "Spam", 2: "AI Phishing", 3: "Uncertain"}


def main() -> None:
    model_path = os.path.join(SCRIPT_DIR, "models", "email_classifier.pkl")

    if not os.path.exists(model_path):
        print(f"ERROR: Model file not found at {model_path}")
        print("If you need to retrain the model run:")
        print("  python -m src.utils.train_model")
        sys.exit(1)

    print("Loading model …")
    classifier = SecureEmailClassifier(model_path)
    print(f"Model loaded from: {model_path}\n")
    print("=" * 70)

    for sample in SAMPLES:
        result = classifier.predict_secure(sample["text"])
        prediction_idx = result["prediction"]
        label = LABEL_MAP.get(prediction_idx, f"Class {prediction_idx}")
        confidence = result["confidence"]
        uncertain = " (uncertain)" if result["is_uncertain"] else ""

        print(f"Sample : {sample['label']}")
        print(f"Result : {label}{uncertain}  (confidence: {confidence:.1f}%)")
        probs = result.get("probabilities", [])
        if probs:
            prob_str = "  |  ".join(
                f"{LABEL_MAP.get(i, i)}: {p * 100:.1f}%"
                for i, p in enumerate(probs)
            )
            print(f"Probs  : {prob_str}")
        print("-" * 70)

    print("\nDone. To start the full web UI run:  make dev  or  ./run-local.sh")


if __name__ == "__main__":
    main()
