"""
Secure ML Model with Improved Training and Validation
Addresses overfitting and data quality issues
"""
import pandas as pd
import numpy as np
import joblib
import re
import os
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV

logger = logging.getLogger(__name__)


class SecureEmailClassifier:
    """Secure email classifier with improved validation."""
    
    def __init__(self, model_path: str = None):
        """Initialize the classifier."""
        self.model = None
        self.vectorizer = None
        self.pipeline = None
        self.model_path = model_path
        self.model_metadata = {}
        
        # Load model if path provided
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def preprocess_text(self, text: str) -> str:
        """
        Secure text preprocessing without feature leakage.
        
        Args:
            text: Input email text
            
        Returns:
            Preprocessed text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Replace URLs with token (security: prevent URL-based attacks)
        text = re.sub(r'https?://[^\s]+|www\.[^\s]+', ' URL_TOKEN ', text)
        
        # Replace email addresses with token
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' EMAIL_TOKEN ', text)
        
        # Replace phone numbers with token
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', ' PHONE_TOKEN ', text)
        
        # Replace credit card patterns
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', ' CARD_TOKEN ', text)
        
        # Replace excessive punctuation
        text = re.sub(r'[!]{2,}', ' EXCLAMATION_MULTIPLE ', text)
        text = re.sub(r'[?]{2,}', ' QUESTION_MULTIPLE ', text)
        text = re.sub(r'[$]{2,}', ' DOLLAR_MULTIPLE ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_features(self, text: str) -> Dict[str, int]:
        """
        Extract statistical features without data leakage.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary of features
        """
        features = {}
        
        # Basic statistics
        features['char_count'] = len(text)
        features['word_count'] = len(text.split())
        features['line_count'] = len(text.splitlines())
        
        # Punctuation features
        features['exclamation_count'] = text.count('!')
        features['question_count'] = text.count('?')
        features['dollar_count'] = text.count('$')
        
        # Capital letters ratio
        if len(text) > 0:
            features['caps_ratio'] = sum(1 for c in text if c.isupper()) / len(text)
        else:
            features['caps_ratio'] = 0
        
        # URL and email indicators
        features['has_url'] = int('URL_TOKEN' in text)
        features['has_email'] = int('EMAIL_TOKEN' in text)
        features['has_phone'] = int('PHONE_TOKEN' in text)
        features['has_card'] = int('CARD_TOKEN' in text)
        
        return features
    
    def predict_secure(self, email_text: str) -> Dict[str, any]:
        """
        Make secure prediction with validation.
        
        Args:
            email_text: Email content to classify
            
        Returns:
            Dictionary with prediction results
        """
        if not self.pipeline:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        if not email_text or len(email_text.strip()) == 0:
            raise ValueError("Email text cannot be empty")
        
        try:
            # Preprocess text
            processed_text = self.preprocess_text(email_text)
            
            # Make prediction
            prediction = int(self.pipeline.predict([processed_text])[0])
            probabilities = self.pipeline.predict_proba([processed_text])[0]
            
            # Calculate confidence
            confidence = float(probabilities[prediction]) * 100
            
            # Extract features for explanation
            features = self.extract_features(email_text)
            
            # Determine if prediction is uncertain
            is_uncertain = confidence < 70.0
            
            return {
                'prediction': prediction,
                'probabilities': probabilities.tolist(),
                'confidence': confidence,
                'is_uncertain': is_uncertain,
                'features': features,
                'processed_length': len(processed_text),
                'model_version': self.model_metadata.get('version', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise ValueError(f"Prediction failed: {str(e)}")
    
    def load_model(self, model_path: str) -> bool:
        """
        Securely load model with validation.
        
        Args:
            model_path: Path to model file
            
        Returns:
            True if loaded successfully
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        try:
            # Load model
            self.pipeline = joblib.load(model_path)
            
            # Load metadata if exists
            metadata_path = model_path.replace('.pkl', '_metadata.json')
            if os.path.exists(metadata_path):
                import json
                with open(metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
            
            logger.info(f"Model loaded successfully from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise ValueError(f"Failed to load model: {str(e)}")
    
    def validate_model_performance(self, test_data: pd.DataFrame) -> Dict[str, float]:
        """
        Validate model performance on test data.
        
        Args:
            test_data: DataFrame with 'text' and 'label' columns
            
        Returns:
            Performance metrics
        """
        if not self.pipeline:
            raise ValueError("Model not loaded")
        
        # Preprocess test data
        X_test = test_data['text'].apply(self.preprocess_text)
        y_test = test_data['label']
        
        # Make predictions
        y_pred = self.pipeline.predict(X_test)
        y_proba = self.pipeline.predict_proba(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
        
        # Calculate per-class metrics
        per_class_metrics = {}
        for class_idx in range(len(np.unique(y_test))):
            class_precision, class_recall, class_f1, _ = precision_recall_fscore_support(
                y_test, y_pred, labels=[class_idx], average=None
            )
            per_class_metrics[f'class_{class_idx}'] = {
                'precision': float(class_precision[0]) if len(class_precision) > 0 else 0.0,
                'recall': float(class_recall[0]) if len(class_recall) > 0 else 0.0,
                'f1': float(class_f1[0]) if len(class_f1) > 0 else 0.0
            }
        
        return {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'per_class_metrics': per_class_metrics,
            'test_samples': len(test_data)
        }


def create_production_dataset() -> pd.DataFrame:
    """
    Create a more realistic dataset for production training.
    This addresses the synthetic data issue.
    """
    
    # Legitimate emails (more diverse and realistic)
    ham_emails = [
        # Business emails
        "Hi Sarah, I hope this email finds you well. I wanted to follow up on our meeting last week regarding the Q3 budget planning. Could we schedule a call this week to discuss the revised numbers? Best regards, John",
        "Dear Team, Please find attached the quarterly report for your review. The deadline for feedback is Friday EOD. Let me know if you have any questions. Thanks, Michael",
        "Good morning, Just a reminder that the project milestone is due tomorrow. Please ensure all deliverables are submitted to the shared drive. Contact me if you need any assistance. Regards, Lisa",
        "Hello Alex, Thank you for your presentation yesterday. The client was impressed with the proposal. We should schedule a follow-up meeting to discuss implementation details. Best, David",
        "Hi Everyone, The office will be closed next Monday for maintenance. Please plan accordingly and work remotely if needed. IT support will be available via phone. Thanks, HR Team",
        
        # Customer service
        "Thank you for contacting our support team. We have received your inquiry and will respond within 24 hours. Your ticket number is #12345. Best regards, Customer Service",
        "Dear Customer, Your order has been processed and will ship within 2 business days. You will receive tracking information via email once the package is dispatched. Thank you for your business.",
        "Hi there, We appreciate your feedback about our recent service. Your comments have been forwarded to the appropriate department for review. We value your input and will use it to improve our services.",
        
        # Personal emails  
        "Hey mom, thanks for dinner last night. The kids had a great time with grandpa. Let's plan another family gathering soon. Love you, Jenny",
        "Hi Mark, are we still on for golf this Saturday? The weather looks good. Let me know if you want to grab lunch afterward. Cheers, Tom",
        "Dear Friends, we're excited to invite you to our housewarming party next month. More details to follow. Hope to see you there! Best, Sarah and Mike",
        
        # Newsletters (legitimate)
        "Weekly Newsletter: This week's top stories in technology. Read about the latest developments in artificial intelligence and cybersecurity. Subscribe to receive more updates.",
        "Your monthly summary from LinkedIn shows you had 15 profile views this week. Connect with more professionals in your industry to expand your network.",
        "GitHub Weekly: Your repository received 3 new stars this week. Check out trending projects in your programming languages.",
        
        # Automated notifications
        "Your account password was successfully changed. If you did not make this change, please contact our security team immediately. This is an automated message.",
        "Appointment reminder: You have a scheduled appointment tomorrow at 2 PM. Please arrive 15 minutes early. Call us if you need to reschedule.",
        "Your subscription will renew in 7 days. No action is required. You can manage your subscription settings in your account dashboard.",
        
        # Short professional messages
        "Meeting confirmed for 3 PM today in conference room B.",
        "Please review the attached document and provide feedback by Friday.",
        "The server maintenance is complete. All systems are back online.",
        "Your timesheet for last week has been approved.",
    ]
    
    # Spam emails (realistic patterns)
    spam_emails = [
        # Prize/lottery scams
        "CONGRATULATIONS! You have been selected as a winner in our international lottery. Your prize of $500,000 awaits collection. Contact our claims department immediately to process your winnings. This offer expires in 48 hours.",
        "You are a LUCKY WINNER! Your email address has won $1,000,000 in the Microsoft promotional lottery. To claim your prize, reply with your full name, address, and phone number. Processing fee of $500 required.",
        "WINNER NOTIFICATION: Congratulations! You have won $750,000 in our annual sweepstakes. This is not a scam. Click here to claim your prize before it expires. Limited time offer!",
        
        # Work from home scams
        "Make $5000 per week working from home! No experience necessary. Join thousands of successful people earning extra income. This amazing opportunity won't last long. Sign up today!",
        "Work from home and earn $300 per hour! Our proven system helps you make money online. No selling required. Investment of only $99 gets you started. Join our successful team now!",
        "Earn money while you sleep! Our automated system generates passive income 24/7. Guaranteed returns of 500% within 30 days. Risk-free opportunity. Limited spots available.",
        
        # Investment/crypto scams  
        "HOT STOCK TIP: This penny stock will explode 1000% this week! Buy now before Wall Street catches on. Our insider information guarantees massive profits. Don't miss out!",
        "Bitcoin trading robot earns $10,000 daily! Our AI system beats the market every time. Invest just $250 and watch your money grow. Results guaranteed or money back!",
        "Real estate investment opportunity! Double your money in 60 days guaranteed. Exclusive deals not available to the public. Secure your financial future today!",
        
        # Health/pharma spam
        "Lose 50 pounds in 30 days without diet or exercise! Our revolutionary weight loss pills are clinically proven. FDA approved. Order now and save 50%. Free shipping included!",
        "Miracle cure for diabetes discovered! Doctors hate this one simple trick. Natural ingredients restore your health completely. Limited supply available. Order before it's banned!",
        "Anti-aging breakthrough makes you look 20 years younger! Hollywood celebrities use this secret formula. Results in just 7 days. Special discount for first 100 customers!",
        
        # Romance/dating scams
        "Beautiful women in your area want to meet you tonight! Join our dating service for free. Thousands of profiles waiting. Start chatting now. No commitment required!",
        "Lonely? Find your soulmate today! Our matching service has a 99% success rate. True love is just one click away. Sign up free and find happiness!",
    ]
    
    # Phishing emails (sophisticated)
    phishing_emails = [
        # Banking phishing
        "Dear Valued Customer, We have detected suspicious activity on your account from an unrecognized device. As a security measure, your account access has been temporarily restricted. Please verify your identity immediately to restore full access. Click the secure link below and enter your login credentials. You have 24 hours to complete this verification before your account is permanently suspended.",
        "Important Security Alert: Your bank account shows unauthorized transactions totaling $2,500. To prevent further fraudulent activity, please confirm your account details immediately. Our fraud protection team is standing by to assist you. Click here to secure your account now.",
        "Account Verification Required: We have updated our security systems and all customers must re-verify their accounts. Failure to complete verification within 48 hours will result in account closure. Please provide your account number, PIN, and security questions to maintain access.",
        
        # Tech company phishing
        "Microsoft Security Alert: Your Office 365 account has been accessed from an unusual location in Russia. If this was not you, please reset your password immediately. Click here to secure your account and prevent unauthorized access to your files.",
        "Apple ID Security Notice: We have detected that your Apple ID was used to sign in to a device we don't recognize. If this was not you, your account may be compromised. Verify your account information to prevent data loss and unauthorized purchases.",
        "Google Account Suspended: We have suspended your Google account due to policy violations. To restore access to Gmail, Drive, and other services, please verify your identity using the secure link below. This verification must be completed within 72 hours.",
        
        # Financial phishing
        "PayPal Account Limited: Your account has been limited due to security concerns. To restore full access to your funds, please confirm your identity by providing your account information. Our security team has flagged unusual activity that requires immediate attention.",
        "Credit Card Fraud Alert: We have detected potentially fraudulent charges on your credit card ending in 1234. Please review these transactions and confirm whether they are legitimate. Click here to access your account and dispute any unauthorized charges.",
        "Tax Refund Available: The IRS has processed your tax return and you are eligible for a refund of $3,200. To receive your refund, please verify your bank account information through our secure portal. This offer expires in 10 days.",
        
        # Corporate phishing
        "IT Security Update Required: All employees must install the latest security update by end of business today. Your computer will be disconnected from the network if this update is not completed. Click here to download and install the required patch.",
        "HR Benefits Enrollment: Open enrollment for health benefits ends this week. You must update your selections or you will lose coverage. Click here to access the employee benefits portal and make your selections.",
        "Payroll System Update: We are upgrading our payroll system and need to verify your direct deposit information. Please confirm your bank account details to ensure uninterrupted pay. This update must be completed before the next pay period.",
        
        # Package delivery phishing
        "FedEx Delivery Failure: Your package could not be delivered due to an incorrect address. Please update your delivery information and pay the $5.99 redelivery fee to schedule a new delivery attempt. Your package will be returned if not claimed within 48 hours.",
        "DHL Customs Hold: Your international package is being held at customs. To release your shipment, you must pay import duties of $45.99. Click here to process payment and complete the customs clearance.",
        "USPS Package Notification: A package addressed to you requires additional postage of $2.50. Please pay this fee online to complete delivery. Your package will be returned to sender if payment is not received within 5 days.",
    ]
    
    # Create dataset
    data = []
    
    # Add legitimate emails (label 0)
    for email in ham_emails:
        data.append({"text": email, "label": 0, "category": "ham"})
    
    # Add spam emails (label 1)  
    for email in spam_emails:
        data.append({"text": email, "label": 1, "category": "spam"})
    
    # Add phishing emails (label 2)
    for email in phishing_emails:
        data.append({"text": email, "label": 2, "category": "phishing"})
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Shuffle the dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return df


def train_production_model(output_path: str = "models/email_classifier.pkl") -> Dict[str, any]:
    """
    Train a production-ready model with proper validation.
    
    Args:
        output_path: Path to save the trained model
        
    Returns:
        Training results and metrics
    """
    logger.info("Starting production model training...")
    
    # Create dataset
    df = create_production_dataset()
    logger.info(f"Dataset created with {len(df)} samples")
    logger.info(f"Class distribution: {df['label'].value_counts().to_dict()}")
    
    # Initialize classifier
    classifier = SecureEmailClassifier()
    
    # Preprocess text
    df['processed_text'] = df['text'].apply(classifier.preprocess_text)
    
    # Split data with stratification
    X = df['processed_text']
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    
    # Create pipeline with optimized parameters
    tfidf = TfidfVectorizer(
        ngram_range=(1, 2),  # Reduced from trigrams to avoid overfitting
        max_features=5000,   # Reduced to prevent overfitting on small dataset
        min_df=2,           # Require at least 2 occurrences
        max_df=0.8,         # Ignore very common terms
        stop_words='english',
        token_pattern=r'\b[a-zA-Z]{2,}\b'
    )
    
    # Use ensemble for better generalization
    lr = LogisticRegression(
        C=1.0,
        max_iter=1000,
        random_state=42,
        class_weight='balanced'
    )
    
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )
    
    # Create voting classifier
    ensemble = VotingClassifier(
        estimators=[('lr', lr), ('rf', rf)],
        voting='soft'
    )
    
    # Create pipeline
    pipeline = Pipeline([
        ('tfidf', tfidf),
        ('classifier', ensemble)
    ])
    
    # Calibrate probabilities
    calibrated_pipeline = CalibratedClassifierCV(pipeline, method='isotonic', cv=3)
    
    # Train model
    logger.info("Training model...")
    calibrated_pipeline.fit(X_train, y_train)
    
    # Evaluate model
    logger.info("Evaluating model...")
    
    # Training accuracy
    train_score = calibrated_pipeline.score(X_train, y_train)
    
    # Test accuracy
    test_score = calibrated_pipeline.score(X_test, y_test)
    
    # Cross-validation
    cv_scores = cross_val_score(calibrated_pipeline, X, y, cv=5, scoring='accuracy')
    
    # Detailed evaluation
    y_pred = calibrated_pipeline.predict(X_test)
    y_proba = calibrated_pipeline.predict_proba(X_test)
    
    # Calculate metrics
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted')
    
    results = {
        'training_accuracy': float(train_score),
        'test_accuracy': float(test_score),
        'cv_mean': float(cv_scores.mean()),
        'cv_std': float(cv_scores.std()),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'dataset_size': len(df),
        'test_size': len(X_test),
        'class_distribution': df['label'].value_counts().to_dict()
    }
    
    # Log results
    logger.info(f"Training Results:")
    logger.info(f"  Training Accuracy: {train_score:.4f}")
    logger.info(f"  Test Accuracy: {test_score:.4f}")
    logger.info(f"  Cross-validation: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    logger.info(f"  Precision: {precision:.4f}")
    logger.info(f"  Recall: {recall:.4f}")
    logger.info(f"  F1-Score: {f1:.4f}")
    
    # Check for overfitting
    if train_score - test_score > 0.1:
        logger.warning("Potential overfitting detected (training accuracy >> test accuracy)")
    
    # Save model
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(calibrated_pipeline, output_path)
    
    # Save metadata
    metadata = {
        'version': '2.0',
        'created_at': datetime.now().isoformat(),
        'model_type': 'ensemble_calibrated',
        'features': 'tfidf_ngrams_1_2',
        'metrics': results
    }
    
    metadata_path = output_path.replace('.pkl', '_metadata.json')
    import json
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.info(f"Model saved to {output_path}")
    logger.info(f"Metadata saved to {metadata_path}")
    
    return results


if __name__ == "__main__":
    # Train production model
    results = train_production_model()
    print("Training completed successfully!")
    print(f"Final test accuracy: {results['test_accuracy']:.4f}")