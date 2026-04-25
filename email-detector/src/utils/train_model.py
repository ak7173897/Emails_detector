"""
=============================================================================
AI Email Security Detector - Model Training Script (Production Ready)
=============================================================================
This script:
1. Generates a comprehensive dataset with diverse email types
2. Includes edge cases: newsletters, marketing, short emails, BEC attempts
3. Uses keyword based detection for spam/phishing words
4. Detects spelling mistakes common in scam emails
5. Saves models using joblib for use in the Flask backend

Key Improvements:
- Comprehensive spam/phishing keyword list
- Spelling mistake detection
- No emojis in output
- 95%+ accuracy target
=============================================================================
"""

import pandas as pd
import numpy as np
import joblib
import re
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.naive_bayes import MultinomialNB


# =============================================================================
# SPAM/PHISHING KEYWORD LISTS
# These words are commonly found in malicious emails
# =============================================================================

SPAM_KEYWORDS = [
    # Money/Prize related
    "winner", "won", "lottery", "prize", "jackpot", "million", "billion",
    "cash", "money", "dollars", "pounds", "euros", "inheritance", "fortune",
    "wealthy", "rich", "millionaire", "billionaire", "free money",
    
    # Urgency words
    "urgent", "immediately", "now", "hurry", "limited", "expires", "deadline",
    "act now", "don't delay", "time sensitive", "last chance", "final notice",
    "only today", "offer ends", "limited time", "rush", "asap",
    
    # Action words
    "click here", "click now", "click below", "sign up", "subscribe",
    "register now", "join now", "apply now", "get started", "order now",
    "buy now", "purchase", "call now", "reply now", "respond immediately",
    
    # Too good to be true
    "free", "bonus", "discount", "save", "cheap", "bargain", "deal",
    "offer", "promotion", "special", "exclusive", "guaranteed", "risk free",
    "no cost", "no obligation", "100% free", "completely free",
    
    # Work from home scams
    "work from home", "earn money", "make money", "income", "salary",
    "job opportunity", "business opportunity", "investment", "profit",
    "passive income", "easy money", "quick cash", "extra income",
    
    # Health/Pharma spam
    "weight loss", "lose weight", "diet", "pills", "medication",
    "prescription", "pharmacy", "drug", "viagra", "cialis", "supplement",
    "miracle", "cure", "treatment", "doctor", "medical",
    
    # Adult/Dating spam
    "dating", "singles", "meet", "lonely", "romance", "relationship",
    "match", "love", "partner", "companion",
    
    # Excessive punctuation patterns
    "!!!", "???", "...", "***", "$$$",
]

PHISHING_KEYWORDS = [
    # Account security
    "verify", "verification", "confirm", "confirmation", "validate",
    "suspended", "restricted", "locked", "disabled", "blocked",
    "unauthorized", "unusual activity", "suspicious", "security alert",
    "security notice", "account access", "account update",
    
    # Credential requests
    "password", "username", "login", "signin", "sign in", "log in",
    "credentials", "ssn", "social security", "credit card", "card number",
    "cvv", "expiration", "billing", "payment details", "bank account",
    "routing number", "pin", "passcode",
    
    # Urgency/Threat
    "will be suspended", "will be terminated", "will be closed",
    "will be deleted", "permanent", "immediately", "within 24 hours",
    "within 48 hours", "failure to", "if you do not", "unless you",
    
    # Trust building
    "dear customer", "dear user", "dear member", "valued customer",
    "valued member", "dear account holder", "dear sir", "dear madam",
    
    # Fake authority
    "security team", "support team", "customer service", "helpdesk",
    "administrator", "it department", "compliance", "legal department",
    
    # Technical deception
    "click the link", "click here to verify", "update your information",
    "confirm your identity", "secure your account", "restore access",
    "reactivate", "unlock your account",
]

# Common misspellings in scam emails
COMMON_MISSPELLINGS = {
    # Intentional misspellings to bypass filters
    "recieve": "receive",
    "reciept": "receipt",
    "adress": "address",
    "accomodation": "accommodation",
    "occured": "occurred",
    "seperate": "separate",
    "definately": "definitely",
    "untill": "until",
    "tommorow": "tomorrow",
    "goverment": "government",
    "offical": "official",
    "accout": "account",
    "acount": "account",
    "secuirty": "security",
    "securty": "security",
    "verifiy": "verify",
    "verfiy": "verify",
    "paypal": "paypal",  # Keep as is
    "payement": "payment",
    "paymnet": "payment",
    "imediately": "immediately",
    "immedietly": "immediately",
    "immediatly": "immediately",
    "suspsended": "suspended",
    "suspened": "suspended",
    "unauthorised": "unauthorized",
    "unauthoried": "unauthorized",
    "confrim": "confirm",
    "confirn": "confirm",
    "informtion": "information",
    "infomation": "information",
    "pasword": "password",
    "passowrd": "password",
    "passwrod": "password",
    "credentails": "credentials",
    "loign": "login",
    "sighn": "sign",
    "clik": "click",
    "clcik": "click",
    "updaet": "update",
    "updtae": "update",
    "activty": "activity",
    "actvity": "activity",
    "resposne": "response",
    "requried": "required",
    "requred": "required",
    "expirng": "expiring",
    "expireing": "expiring",
    "urgnet": "urgent",
    "urgernt": "urgent",
    "mesage": "message",
    "messege": "message",
    "acces": "access",
    "acccess": "access",
    "importent": "important",
    "impotant": "important",
    "securley": "securely",
    "permanetly": "permanently",
    "permanantly": "permanently",
}

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: COMPREHENSIVE DATASET
# Includes: Professional emails, newsletters, marketing, short messages,
# automated notifications, and edge cases that commonly cause false positives
# ─────────────────────────────────────────────────────────────────────────────

# LEGITIMATE EMAILS (HAM) - Diverse categories
HAM_EMAILS = [
    # === PROFESSIONAL/BUSINESS EMAILS ===
    "Hi John, hope you're doing well. I wanted to follow up on the project proposal we discussed last week. Can we schedule a meeting?",
    "Please find attached the quarterly report for your review. Let me know if you have any questions or need clarification.",
    "Thanks for your email. I'll review the documents and get back to you by end of week.",
    "Dear team, the meeting scheduled for Monday has been moved to Tuesday at 2 PM. Please update your calendars.",
    "Hi Sarah, I enjoyed our conversation at the conference. Let's keep in touch and explore potential collaboration.",
    "Good morning! Just checking in to see how the onboarding process is going for the new team members.",
    "Attached is the invoice for services rendered in November. Payment is due within 30 days.",
    "The board has approved the new budget for Q1. Please distribute this to your department heads.",
    "Thank you for attending today's training session. The slides and recording will be shared within 48 hours.",
    "Please submit your timesheets by end of day Thursday. HR needs them to process payroll.",
    "We are pleased to inform you that your leave request has been approved for the dates requested.",
    "Hi everyone, please welcome our new colleague joining the marketing team starting Monday.",
    "Following up on our call. I've drafted the proposal and would love your feedback before we send it.",
    "Can you review the attached contract and let me know your thoughts? No rush on this one.",
    "The project deadline has been extended by one week. Please coordinate with your team accordingly.",
    "Hi, just wanted to share the minutes from yesterday's meeting. Please review and let me know if anything was missed.",
    "The committee has reviewed your proposal and would like to schedule a discussion.",
    "Could you please review the attached presentation before the board meeting next week?",
    "I wanted to share some exciting updates about our department restructuring and new team goals.",
    "I've reviewed the budget proposal and have a few suggestions. Can we discuss this week?",
    
    # === NEWSLETTERS AND MARKETING (Legitimate) ===
    "Weekly Newsletter: Top 10 productivity tips for remote workers. Read more on our blog.",
    "Your monthly summary from LinkedIn: You appeared in 50 searches this week.",
    "New articles from Medium: Stories we think you'll love based on your reading history.",
    "GitHub notification: Your repository has reached 100 stars! Thank you for your contributions.",
    "Spotify Weekly: Discover your personalized playlist with 30 new songs.",
    "Netflix: New releases this month including the shows you've been waiting for.",
    "Amazon: Your order has shipped! Track your package with the link below.",
    "Airbnb: Complete your review for your recent stay in Paris.",
    "Uber Eats: Your food is on the way! Estimated arrival: 25 minutes.",
    "DoorDash: Rate your recent order and earn rewards points.",
    "Your Duolingo reminder: Don't break your streak! Practice Spanish today.",
    "Grammarly Weekly Report: You were more productive than 90% of users.",
    "Notion: Check out our latest templates to boost your workflow.",
    "Slack: Weekly activity digest for your workspace.",
    "Zoom: Your meeting recording is now available to view.",
    "Dropbox: Your shared folder was updated by a collaborator.",
    "Google Photos: Your memories from this day 3 years ago.",
    "Apple: Your App Store receipt for your recent purchase.",
    "Microsoft 365: Your subscription will renew in 30 days.",
    "Adobe Creative Cloud: New updates available for Photoshop and Illustrator.",
    
    # === AUTOMATED SYSTEM NOTIFICATIONS (Legitimate) ===
    "Your password was successfully changed. If you did not make this change, contact support.",
    "Login notification: Your account was accessed from a new device in New York.",
    "Two factor authentication has been enabled on your account.",
    "Your subscription renewal is due next month. No action is required at this time.",
    "System maintenance scheduled for this Saturday from 2 AM to 4 AM.",
    "Your account statement is now available for download in your online banking portal.",
    "We wanted to update you on the progress of your support ticket. Our team is actively working on the issue.",
    "Your flight booking confirmation is attached. Safe travels!",
    "Your library books are due back this Friday. Renew online to avoid late fees.",
    "Your prescription is ready for pickup at our pharmacy. Please bring a valid ID.",
    "Appointment reminder: You have a scheduled appointment tomorrow at 3 PM.",
    "Your package has been delivered and left at the front door.",
    "Payment received: Thank you for your payment of $50.00.",
    "Your report is ready to download from the portal.",
    "Backup completed successfully. All files have been saved.",
    
    # === PERSONAL/CASUAL EMAILS ===
    "Hey! Want to grab coffee later this week? It's been a while since we caught up.",
    "Happy birthday! Hope you have a wonderful day filled with joy.",
    "Thanks for dinner last night. We had a great time!",
    "Let me know when you're free to catch up. Miss hanging out with you.",
    "Photos from the party are attached. Some great memories!",
    "Congrats on the new job! So happy for you.",
    "Can you pick up milk on your way home?",
    "Running late. Be there in 15 minutes.",
    "The kids had a great time at the playdate. Let's do it again soon.",
    "Thanks for the recommendation. I loved that book!",
    
    # === SHORT EMAILS (Edge cases) ===
    "Got it, thanks!",
    "Sounds good.",
    "See you tomorrow.",
    "Perfect, thanks for confirming.",
    "Will do.",
    "On my way.",
    "Received, thank you.",
    "Noted.",
    "Looking forward to it.",
    "Great job on the project!",
    "Meeting confirmed for 3 PM.",
    "Attachment received.",
    "Thanks for the update.",
    "Works for me.",
    "Count me in!",
    
    # === URGENT BUT LEGITIMATE EMAILS ===
    "URGENT: Please submit your timesheet by 5 PM today for payroll processing.",
    "Action Required: Complete your compliance training before the deadline.",
    "Reminder: Your project proposal is due tomorrow. Please submit by EOD.",
    "Important: Office closure notice for the upcoming holiday.",
    "Please respond ASAP: Client needs confirmation by end of day.",
    "Time sensitive: Contract requires your signature before Friday.",
    "Immediate attention needed: Server maintenance tonight at midnight.",
    "Quick turnaround needed: Please review and approve the budget.",
]

SPAM_EMAILS = [
    # === CLASSIC PRIZE/LOTTERY SCAMS ===
    "CONGRATULATIONS! You've been selected as our LUCKY WINNER! Claim your $1,000,000 prize NOW! Click here immediately!",
    "You have WON the UK National Lottery! Your email was randomly selected! Claim 850,000 pounds today!",
    "URGENT LOTTERY WINNER NOTIFICATION: Congratulations! You've won! Contact us within 48 hours!",
    "Your email has won 2,500,000 pounds in the Microsoft Lottery Draw! Contact us to claim!",
    "FREE iPhone 15 Pro! You are our 1,000,000th visitor! Click here to claim your prize now!",
    "CONGRATULATIONS! You won a FREE vacation to the Bahamas! Claim now!",
    "You've been randomly selected to receive a $500 gift card! Complete a short survey to claim!",
    "Winner notification: You have won $50,000 in our promotional draw! Claim immediately!",
    
    # === WORK FROM HOME/MONEY SCAMS ===
    "Make $5000 per week working from home! No experience needed! Join thousands who are already making money!",
    "Work from home and earn $300 per hour! No skills required! Join our network today!",
    "Get rich quick with crypto! Invest just $100 and make $10,000 in 7 days! Limited time offer!",
    "Make millions trading forex! Our robot does all the work! Sign up FREE today!",
    "Become a millionaire with our proven investment system! Guaranteed returns of 500%!",
    "Make passive income online! Our automated system earns money while you sleep! Join now!",
    "Double your money in 24 hours! Bitcoin investment opportunity! Risk free guaranteed!",
    "Secret shopper opportunity! Get paid $200 to shop at local stores!",
    "Make $10,000 weekly with this ONE simple trick! Click to learn more!",
    "Hot investment tip: Buy this stock before it goes 10000% up!",
    "HOT STOCK TIP: This penny stock will explode 1000% this week! Buy NOW before it's too late!",
    
    # === PHARMACEUTICAL/HEALTH SCAMS ===
    "FREE VIAGRA! Buy cheap medications online! No prescription required! Lowest prices guaranteed!",
    "Herbal enlargement pills! 100% natural! Works in just 3 days! Shipped discreetly!",
    "Lose 30 pounds in 30 days! Doctors HATE this one weird trick! 100% guaranteed results!",
    "Miracle cure for diabetes, cancer, and arthritis! 100% natural! Works guaranteed!",
    "Discount pharmacy online! 80% off all medications! No prescription needed! Order today!",
    "Cheap prescription drugs shipped overnight! No questions asked!",
    "Weight loss breakthrough! Lose 50 pounds without diet or exercise!",
    "Anti aging miracle: Look 20 years younger overnight! Celebrities use this secret method!",
    "Acai berry detox cleanse! Lose weight fast! Order now and save!",
    
    # === DATING/ADULT SCAMS ===
    "HOT SINGLES IN YOUR AREA want to meet you! Click here to see who's interested RIGHT NOW!",
    "ADULT DATING: Meet lonely singles in your city tonight! 100% free to join!",
    "Meet beautiful women seeking relationships! Join our dating service!",
    "Lonely women in your area want to meet you NOW! Free signup!",
    
    # === NIGERIAN PRINCE/INHERITANCE SCAMS ===
    "Nigerian Prince needs your help! I have $45 million dollars to transfer and will give you 40% for helping!",
    "RE: Your inheritance claim. Our records show you are the beneficiary of a large estate.",
    "You are selected! Business proposal worth $12.5 million waiting for a trusted partner!",
    "Confidential business proposal: Help transfer $20 million and earn 30% commission.",
    
    # === FAKE URGENCY/THREAT SCAMS ===
    "FINAL NOTICE: Your account will be TERMINATED unless you respond within 24 hours! ACT NOW!",
    "URGENT: Your computer has been infected with a virus! Call us immediately!",
    "WARNING: We have detected suspicious activity on your account! Secure it now!",
    "Your computer is broadcasting your IP address! Hackers can see everything! Fix now!",
    "Your computer has 47 viruses! Download our FREE antivirus now!",
    "FINAL ATTEMPT: Your warranty has expired! Protect your vehicle! Call now!",
    
    # === LOAN/CREDIT SCAMS ===
    "You've been pre approved for a $50,000 loan regardless of your credit score! Apply now!",
    "FREE credit report! See your score now! No credit card required! Check in 30 seconds!",
    "Debt consolidation: Clear all debts for pennies on the dollar! Guaranteed! Free consultation!",
    "Bad credit? No problem! Get approved for a $25,000 loan today!",
    
    # === PRODUCT/SERVICE SCAMS ===
    "Cheap Rolex watches! 90% off retail price! Authentic looking luxury watches shipped worldwide!",
    "Replica handbags, shoes and watches! Top quality at unbeatable prices! Worldwide shipping!",
    "MEGA SALE: 99% discount on all software! Microsoft Office, Adobe Suite for FREE!",
    "SPECIAL OFFER: Buy one get five FREE! Limited stock available! Order in the next 10 minutes!",
    
    # === GAMBLING SCAMS ===
    "Casino bonus: Deposit $50 get $500 FREE! Play slots and win big! Limited time!",
    "Online casino: Win big money from home! $1000 welcome bonus! Sign up now!",
    
    # === SURVEY/GIFT CARD SCAMS ===
    "Get paid to take surveys! Earn up to $500 per day! Sign up free and start earning!",
    "FREE GIFT CARD: Walmart, Amazon, Target! Survey complete in 2 minutes! Claim yours now!",
    "Complete this survey and win a $1000 Amazon gift card! Only takes 2 minutes!",
    
    # === MLM/PYRAMID SCAMS ===
    "MLM opportunity: Join our team and earn residual income forever! Be your own boss!",
    "Join our network and earn unlimited commissions! No selling required!",
    "Work from home business opportunity! Earn $10,000 per month! Limited spots available!",
    
    # === ADDITIONAL SPAM PATTERNS ===
    "Your prize of $500,000 is waiting! Pay small fee to claim!",
    "YOU HAVE BEEN CHOSEN! Exclusive members only deal inside!",
    "Free trial offer! Cancel anytime! Credit card required for verification only!",
    "Exclusive deal just for you! 90% off everything! Today only!",
    "Your recent payment failed! Update your billing information to avoid service interruption!",
]

AI_PHISHING_EMAILS = [
    # === ACCOUNT SECURITY PHISHING ===
    "Dear valued customer, we have detected unusual activity on your account. As a security measure, please verify your identity by clicking the link below and entering your credentials. Failure to do so within 24 hours will result in account suspension.",
    "Hello, I am contacting you from the IT Security department. We have identified a potential breach in your account. To protect your data, please immediately log in through our secure portal and update your password. This is urgent and time sensitive.",
    "Your Microsoft Office 365 subscription has been flagged for suspicious activity. To prevent unauthorized access, please verify your account information by clicking the secure link provided. Our security team is standing by to assist you.",
    "We have noticed that your Google account was accessed from an unfamiliar device in another country. If this was not you, please immediately secure your account by verifying your identity at the link below.",
    "Dear account holder, your bank has temporarily limited your online access due to security concerns. To restore full access, please verify your identity by providing your account number and PIN through our secure verification portal.",
    "Important notification: Your Apple ID has been used to make a purchase of $299.99. If you did not authorize this transaction, please click here immediately to cancel and secure your account.",
    "This is an automated security alert from your email provider. We have detected that your account may have been compromised. Please verify your account credentials within the next 12 hours to avoid permanent suspension.",
    "Your Amazon account has been temporarily suspended due to suspicious purchasing activity. To restore access and protect your payment methods, please verify your information through our secure customer portal immediately.",
    "Alert: An unauthorized attempt was made to reset your password from a device in Eastern Europe. If this was not you, please verify your account immediately by clicking the link and confirming your identity.",
    
    # === PAYMENT/FINANCIAL PHISHING ===
    "Your PayPal account has been limited due to policy violations. Submit the required documentation through our secure form to restore full access to your funds.",
    "Dear customer, your credit card ending in 4242 has been charged $847.00 for an international transaction. If you did not authorize this charge, please verify your identity through the secure link to initiate a dispute.",
    "Your Netflix payment has failed and your subscription will be cancelled within 48 hours. To continue enjoying unlimited streaming, please update your payment information through our secure billing portal immediately.",
    "Your Spotify account subscription has been cancelled due to a payment failure. To restore your premium music experience, please update your billing information through our secure payment portal.",
    "Your recent transfer of $5,000 is pending verification. Please confirm the transaction by logging into your account through our secure banking portal.",
    "Your Coinbase wallet has been accessed from an unrecognized IP address. To secure your cryptocurrency holdings, please verify your identity and confirm your wallet information through our secure verification portal.",
    
    # === CORPORATE/HR PHISHING ===
    "Dear team member, the HR department requires all employees to update their direct deposit information in our new payroll system by end of business today. Please click the link and enter your banking details to ensure uninterrupted payment.",
    "This is an important message from your IT administrator. We are upgrading our email servers and all users must re authenticate their accounts by today. Please click the link and enter your work email and password to maintain access.",
    "We noticed you haven't completed your annual security training. Your network access will be revoked in 2 hours unless you complete the training at the link below using your corporate credentials.",
    "The HR department requires you to update your W2 information for tax purposes. Please submit your Social Security Number and date of birth through our secure employee portal.",
    "Dear colleague, I am reaching out regarding an urgent wire transfer that needs to be completed today. Our CEO is traveling and has asked me to coordinate this. Please process a transfer of $25,000 to the following account immediately.",
    
    # === DELIVERY/PACKAGE PHISHING ===
    "Your DHL package delivery has failed because the delivery address was incomplete. To reschedule delivery and avoid return shipping, please confirm your address and pay the nominal redelivery fee through our secure payment link.",
    "Your package from an online retailer is being held at customs. To release your package, you must pay an import duty of $45 through our secure payment link. Failure to pay within 48 hours will result in the package being returned.",
    "USPS Notification: Your package could not be delivered. Please verify your shipping address and pay the $3.99 redelivery fee to schedule a new delivery attempt.",
    "FedEx Alert: A package addressed to you is awaiting confirmation. Please verify your identity and confirm delivery preferences through our secure tracking portal.",
    
    # === DOCUMENT/SIGNATURE PHISHING ===
    "You have received a secure document via DocuSign that requires your immediate signature. This document is time sensitive and contains important legal information. Please click the link to view and sign the document using your credentials.",
    "Action required: A shared document requires your review and approval. Click here to access the secure document portal and provide your authentication.",
    "Important contract awaiting your signature. Please log in to our secure document portal to review and sign the attached agreement.",
    
    # === SOCIAL MEDIA PHISHING ===
    "Your LinkedIn profile has been viewed by a recruiter offering a position with a salary of $150,000 per year. To view this opportunity and connect with the recruiter, please verify your account by clicking the link.",
    "Your Facebook account has been reported for violating community standards. To avoid account suspension, please verify your identity through our secure verification portal within 24 hours.",
    "Instagram Security: Unusual login detected. Please confirm your identity to prevent account lockout.",
    "Your Zoom account has been flagged for sending inappropriate content. To appeal this decision and restore your account, please verify your identity and provide your account credentials through our review portal.",
    
    # === GOVERNMENT/TAX PHISHING ===
    "This message is from the IRS Tax Division. Our records indicate you are eligible for a tax refund of $3,500. To process your refund, you must verify your Social Security Number and banking information through our secure government portal.",
    "We are contacting you on behalf of the Social Security Administration. There is a hold on your Social Security number due to suspicious activity. Please call our toll free number immediately to resolve this issue.",
    "Congratulations! Your application for the government relief fund has been approved. You are entitled to receive $1,400 in assistance. Please provide your banking information through the secure government portal.",
    
    # === HEALTHCARE PHISHING ===
    "Your health insurance claim has been processed and you are eligible for a reimbursement of $2,340. To receive your payment, please verify your identity and provide your bank account details through our secure healthcare portal.",
    "Medicare Alert: Your benefits require immediate verification. Please confirm your Medicare ID and personal information to continue receiving coverage.",
    
    # === CLOUD/STORAGE PHISHING ===
    "Security alert: Your email account storage is 99% full and will be deactivated within 24 hours. To prevent loss of emails, please click the verification link and enter your login credentials to upgrade your storage capacity.",
    "Your Dropbox account has been accessed from a new location. If this wasn't you, please immediately verify your account credentials through the link below to secure your files.",
    "URGENT: Your iCloud storage is full and your photos will be deleted. Click here to verify your Apple ID and upgrade your storage plan to prevent data loss.",
    "OneDrive Security: Suspicious activity detected. Please verify your Microsoft account credentials to prevent data loss.",
    
    # === DOMAIN/WEBSITE PHISHING ===
    "Important: Your domain name is about to expire in 24 hours. To prevent your website from going offline and losing your domain permanently, please renew immediately by clicking the link.",
    "Your website hosting will be suspended due to unpaid invoices. Please update your payment information immediately to avoid service interruption.",
    
    # === DATA BREACH PHISHING ===
    "Dear user, our security system has detected that your account password was recently exposed in a data breach. To protect your account, please immediately change your password by clicking the secure link.",
    "Security notification: We have detected that your email account is being used to send spam without your knowledge. To stop this activity and secure your account, please verify your credentials through the link immediately.",
    "We have detected that someone is using your email address to send phishing emails. Your account will be blocked unless you verify your identity within the next hour.",
    "Important: Your two factor authentication has been disabled on your account. If you did not make this change, please immediately re enable security features by verifying your identity through our secure authentication portal.",
    
    # === ORDER/PURCHASE PHISHING ===
    "Your order #8827364 has been placed for $1,299.99. If you did not authorize this purchase, click here immediately to cancel and verify your account information.",
    "Amazon Order Confirmation: Your purchase of $899.99 is being processed. If you did not make this purchase, please verify your account immediately.",
    "We detected a login from Moscow, Russia on your account. If this wasn't you, please secure your account immediately by resetting your password at the link below.",
    
    # === LOAN/FINANCIAL PHISHING ===
    "We are reaching out regarding your recent application for a business loan. Congratulations, you have been pre approved for $50,000. To complete the process, please verify your identity and banking information through our secure portal.",
    "Your loan application has been approved. To receive your funds, please verify your bank account information and identity through our secure verification portal.",
]


# =============================================================================
# SECTION 2: TEXT PREPROCESSING WITH SPELL CHECK
# =============================================================================

STOPWORDS = set([
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","yourselves","he","him","his","himself","she","her","hers",
    "herself","it","its","itself","they","them","their","theirs","themselves",
    "what","which","who","whom","this","that","these","those","am","is","are",
    "was","were","be","been","being","have","has","had","having","do","does",
    "did","doing","a","an","the","and","but","if","or","because","as","until",
    "while","of","at","by","for","with","about","against","between","into",
    "through","during","before","after","above","below","to","from","up","down",
    "in","out","on","off","over","under","again","further","then","once","here",
    "there","when","where","why","how","all","both","each","few","more","most",
    "other","some","such","no","nor","not","only","own","same","so","than","too",
    "very","s","t","can","will","just","don","should","now","d","ll","m","o",
    "re","ve","y","ain","aren","couldn","didn","doesn","hadn","hasn","haven",
    "isn","ma","mightn","mustn","needn","shan","shouldn","wasn","weren","won","wouldn"
])


def count_spam_keywords(text):
    """Count number of spam keywords in text."""
    text_lower = text.lower()
    count = 0
    for keyword in SPAM_KEYWORDS:
        if keyword.lower() in text_lower:
            count += 1
    return count


def count_phishing_keywords(text):
    """Count number of phishing keywords in text."""
    text_lower = text.lower()
    count = 0
    for keyword in PHISHING_KEYWORDS:
        if keyword.lower() in text_lower:
            count += 1
    return count


def count_misspellings(text):
    """Count common scam misspellings in text."""
    text_lower = text.lower()
    count = 0
    for misspelled in COMMON_MISSPELLINGS.keys():
        if misspelled in text_lower:
            count += 1
    return count


def count_excessive_punctuation(text):
    """Count excessive punctuation patterns common in spam."""
    patterns = [
        r'!{2,}',  # Multiple exclamation marks
        r'\?{2,}',  # Multiple question marks
        r'\.{3,}',  # Ellipsis or more dots
        r'\${2,}',  # Multiple dollar signs
        r'\*{2,}',  # Multiple asterisks
    ]
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, text))
    return count


def count_all_caps_words(text):
    """Count words that are all caps (shouting)."""
    words = text.split()
    caps_words = [w for w in words if len(w) > 2 and w.isupper()]
    return len(caps_words)


def preprocess_text(text):
    """
    Preprocess email text:
    1. Lowercase
    2. Remove URLs
    3. Remove special characters
    4. Tokenize
    5. Remove stopwords
    6. Add feature markers for spam/phishing indicators
    """
    original_text = text
    
    # Count features before cleaning
    spam_kw_count = count_spam_keywords(original_text)
    phishing_kw_count = count_phishing_keywords(original_text)
    misspelling_count = count_misspellings(original_text)
    excessive_punct_count = count_excessive_punctuation(original_text)
    caps_count = count_all_caps_words(original_text)
    
    # Lowercase
    text = text.lower()
    
    # Remove URLs but mark their presence
    has_url = bool(re.search(r'http\S+|www\S+|https\S+', text))
    text = re.sub(r'http\S+|www\S+|https\S+', ' urltoken ', text, flags=re.MULTILINE)
    
    # Remove email addresses but mark their presence
    has_email = bool(re.search(r'\S+@\S+', text))
    text = re.sub(r'\S+@\S+', ' emailtoken ', text)
    
    # Remove phone numbers
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', ' phonetoken ', text)
    
    # Remove special characters and numbers (keep spaces)
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Tokenize
    tokens = text.split()
    
    # Remove stopwords and short tokens
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 2]
    
    # Add feature markers based on counts
    if spam_kw_count >= 3:
        tokens.extend(['spamkeywordshigh'] * min(spam_kw_count // 2, 5))
    elif spam_kw_count >= 1:
        tokens.append('spamkeywordslow')
    
    if phishing_kw_count >= 3:
        tokens.extend(['phishingkeywordshigh'] * min(phishing_kw_count // 2, 5))
    elif phishing_kw_count >= 1:
        tokens.append('phishingkeywordslow')
    
    if misspelling_count >= 2:
        tokens.extend(['misspellingdetected'] * min(misspelling_count, 3))
    
    if excessive_punct_count >= 3:
        tokens.append('excessivepunctuation')
    
    if caps_count >= 5:
        tokens.append('shoutingdetected')
    
    return ' '.join(tokens)


# =============================================================================
# SECTION 3: DATASET BUILDING
# =============================================================================

def build_dataset():
    """Build combined dataset with three categories with smart augmentation."""
    data = []
    
    # Ham = 0
    for email in HAM_EMAILS:
        data.append({"text": email, "label": 0, "label_name": "Ham (Safe)"})
    
    # Spam = 1  
    for email in SPAM_EMAILS:
        data.append({"text": email, "label": 1, "label_name": "Spam"})
    
    # AI Phishing = 2
    for email in AI_PHISHING_EMAILS:
        data.append({"text": email, "label": 2, "label_name": "AI Phishing"})

    # Minimal augmentation to avoid data leakage
    # Only add variations that would realistically occur
    augmented = []
    
    for row in data:
        # Add FWD/RE prefix (common in real emails)
        if row["label"] == 0:  # Only for ham emails
            augmented.append({
                "text": "FWD: " + row["text"],
                "label": row["label"],
                "label_name": row["label_name"]
            })
    
    data.extend(augmented)
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=["text"])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df


# =============================================================================
# SECTION 4: MODEL TRAINING
# =============================================================================

def train_and_save_model():
    print("=" * 60)
    print("AI Email Security Detector - Model Training")
    print("=" * 60)
    
    # Build dataset
    print("\n[1/6] Building dataset...")
    df = build_dataset()
    print(f"    Total samples: {len(df)}")
    print(f"    Ham:          {len(df[df.label == 0])}")
    print(f"    Spam:         {len(df[df.label == 1])}")
    print(f"    AI Phishing:  {len(df[df.label == 2])}")
    
    # Save dataset
    os.makedirs("dataset", exist_ok=True)
    df.to_csv("dataset/emails.csv", index=False)
    print("    Dataset saved to dataset/emails.csv")
    
    # Preprocess
    print("\n[2/6] Preprocessing text...")
    df["processed"] = df["text"].apply(preprocess_text)
    
    # Remove any empty processed texts
    df = df[df["processed"].str.len() > 0]
    
    # Train/test split with stratification
    print("\n[3/6] Splitting data...")
    X = df["processed"]
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"    Training: {len(X_train)} samples")
    print(f"    Testing:  {len(X_test)} samples")
    
    # Build optimized pipeline with better TF-IDF settings
    print("\n[4/6] Training model with optimized parameters...")
    
    # Enhanced TF-IDF vectorizer
    tfidf = TfidfVectorizer(
        ngram_range=(1, 3),        # unigrams + bigrams + trigrams
        max_features=15000,
        min_df=1,
        max_df=0.95,               # Ignore terms that appear in >95% of docs
        sublinear_tf=True,
        strip_accents='unicode',
        analyzer='word',
        token_pattern=r'\b[a-zA-Z]{2,}\b',  # Only words with 2+ letters
        use_idf=True,
        smooth_idf=True
    )
    
    # Logistic Regression with optimized hyperparameters
    lr_clf = LogisticRegression(
        C=5.0,                     # Regularization strength
        max_iter=2000,
        random_state=42,
        solver='lbfgs',
        class_weight='balanced',
        penalty='l2'
    )
    
    pipeline = Pipeline([
        ('tfidf', tfidf),
        ('clf', lr_clf)
    ])
    
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    print("\n[5/6] Evaluating model...")
    y_pred = pipeline.predict(X_test)
    y_pred_train = pipeline.predict(X_train)
    
    train_acc = accuracy_score(y_train, y_pred_train)
    test_acc = accuracy_score(y_test, y_pred)
    
    print(f"\n    Training Accuracy: {train_acc:.4f} ({train_acc*100:.2f}%)")
    print(f"    Test Accuracy:     {test_acc:.4f} ({test_acc*100:.2f}%)")
    
    print("\n    Classification Report (Test Set):")
    print(classification_report(y_test, y_pred, 
                                 target_names=["Ham (Safe)", "Spam", "AI Phishing"],
                                 zero_division=0))
    
    # Confusion matrix
    print("    Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"    {cm}")
    
    # Cross-validation with stratified k-fold
    print("\n[6/6] Running cross-validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X, y, cv=cv, scoring='accuracy')
    print(f"    5-Fold CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(f"    CV Scores: {[f'{s:.4f}' for s in cv_scores]}")
    
    # Save model
    os.makedirs("models", exist_ok=True)
    joblib.dump(pipeline, "models/email_classifier.pkl")
    print("\n    Model saved to models/email_classifier.pkl")
    
    # Also save a copy at root level for Flask
    joblib.dump(pipeline, "model.pkl")
    print("    Model also saved to model.pkl")
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    if test_acc >= 0.95:
        print(f"[SUCCESS] Accuracy ({test_acc*100:.1f}%) meets the >95% requirement!")
    elif test_acc >= 0.90:
        print(f"[OK] Accuracy ({test_acc*100:.1f}%) meets the >90% requirement!")
    else:
        print(f"[WARNING] Accuracy ({test_acc*100:.1f}%) is below 90%. Consider more data.")
    print("=" * 60)
    
    return pipeline, test_acc


if __name__ == "__main__":
    train_and_save_model()
