"""
Secure Input Validation and Sanitization
Prevents XSS, injection attacks, and validates all inputs
"""
import re
import html
import bleach
from typing import Optional, Dict, Any
from werkzeug.datastructures import FileStorage


class ValidationError(Exception):
    """Custom validation error."""
    pass


class InputValidator:
    """Secure input validation and sanitization."""
    
    # Allowed HTML tags (very restrictive)
    ALLOWED_TAGS = []
    ALLOWED_ATTRIBUTES = {}
    
    # Email validation pattern
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Safe filename pattern
    SAFE_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 50000) -> str:
        """
        Sanitize text input to prevent XSS.
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
            
        Raises:
            ValidationError: If input is invalid
        """
        if not isinstance(text, str):
            raise ValidationError("Input must be a string")
        
        if len(text) > max_length:
            raise ValidationError(f"Text too long (max {max_length} characters)")
        
        if len(text.strip()) == 0:
            raise ValidationError("Text cannot be empty")
        
        # Remove any HTML tags and escape special characters
        sanitized = bleach.clean(text, tags=InputValidator.ALLOWED_TAGS)
        sanitized = html.escape(sanitized)
        
        return sanitized.strip()
    
    @staticmethod
    def validate_email_content(content: str) -> Dict[str, Any]:
        """
        Validate and sanitize email content.
        
        Args:
            content: Raw email content
            
        Returns:
            Dict with sanitized content and metadata
            
        Raises:
            ValidationError: If content is invalid
        """
        # Basic validation
        if not content or not isinstance(content, str):
            raise ValidationError("Email content is required")
        
        content = content.strip()
        
        if len(content) < 10:
            raise ValidationError("Email content too short (minimum 10 characters)")
        
        if len(content) > 50000:
            raise ValidationError("Email content too long (maximum 50,000 characters)")
        
        # Check for potential binary content
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            raise ValidationError("Invalid character encoding")
        
        # Sanitize content
        sanitized_content = InputValidator.sanitize_text(content)
        
        # Extract metadata
        word_count = len(sanitized_content.split())
        char_count = len(sanitized_content)
        line_count = len(sanitized_content.splitlines())
        
        return {
            'content': sanitized_content,
            'word_count': word_count,
            'char_count': char_count,
            'line_count': line_count,
            'is_valid': True
        }
    
    @staticmethod
    def validate_file_upload(file: FileStorage, allowed_extensions: set) -> Dict[str, Any]:
        """
        Validate uploaded file.
        
        Args:
            file: Uploaded file object
            allowed_extensions: Set of allowed file extensions
            
        Returns:
            Dict with file info and validation status
            
        Raises:
            ValidationError: If file is invalid
        """
        if not file:
            raise ValidationError("No file provided")
        
        if not file.filename:
            raise ValidationError("Invalid filename")
        
        # Check file extension - prevent double extensions like file.txt.exe
        filename = file.filename.lower()
        if '.' not in filename:
            raise ValidationError("File must have an extension")
        
        # Split all extensions and validate each one
        parts = filename.split('.')
        if len(parts) > 2:
            # Multiple extensions detected - only allow safe combinations
            for ext in parts[1:]:
                if ext not in allowed_extensions and ext not in {'', }:
                    raise ValidationError(f"Multiple extensions not allowed: {filename}")
        
        extension = parts[-1]
        if extension not in allowed_extensions:
            raise ValidationError(f"File type not allowed. Allowed: {', '.join(allowed_extensions)}")
        
        # Validate filename safety
        safe_name = InputValidator.sanitize_filename(file.filename)
        
        # Check for null bytes (path traversal attempt)
        if '\x00' in file.filename or '\x00' in safe_name:
            raise ValidationError("Invalid filename characters detected")
        
        return {
            'original_filename': file.filename,
            'safe_filename': safe_name,
            'extension': extension,
            'content_type': file.content_type,
            'is_valid': True
        }
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Create a safe filename.
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        if not filename:
            return 'unnamed_file.txt'
        
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Remove dangerous characters
        safe_chars = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Limit length
        if len(safe_chars) > 100:
            name, ext = safe_chars.rsplit('.', 1) if '.' in safe_chars else (safe_chars, '')
            safe_chars = name[:95] + ('.' + ext if ext else '')
        
        return safe_chars or 'unnamed_file.txt'
    
    @staticmethod
    def validate_json_request(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate JSON request data.
        
        Args:
            data: JSON data from request
            
        Returns:
            Validated data
            
        Raises:
            ValidationError: If data is invalid
        """
        if not isinstance(data, dict):
            raise ValidationError("Invalid JSON format")
        
        # Check for required fields based on endpoint
        validated = {}
        
        if 'text' in data:
            validated['text'] = InputValidator.sanitize_text(data['text'])
        
        if 'reported_label' in data:
            label = data['reported_label']
            if not isinstance(label, int) or label not in [0, 1, 2]:
                raise ValidationError("Invalid reported_label (must be 0, 1, or 2)")
            validated['reported_label'] = label
        
        if 'original_prediction' in data:
            pred = data['original_prediction']
            if not isinstance(pred, int) or pred not in [0, 1, 2]:
                raise ValidationError("Invalid original_prediction (must be 0, 1, or 2)")
            validated['original_prediction'] = pred
        
        return validated
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """
        Validate IP address format.
        
        Args:
            ip: IP address string
            
        Returns:
            True if valid IP address
        """
        if not ip:
            return False
        
        # Basic IPv4 validation
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        try:
            for part in parts:
                if not (0 <= int(part) <= 255):
                    return False
            return True
        except ValueError:
            return False