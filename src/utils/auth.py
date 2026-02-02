"""
Authentication Utilities - Password Hashing & JWT Tokens

This module provides:
1. Password hashing using bcrypt
2. JWT token generation and verification
3. User authentication helpers

For Beginners:
- Password hashing = Converting passwords to unreadable strings
- JWT (JSON Web Token) = Secure way to identify logged-in users
- Never store passwords in plain text!
"""

import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class PasswordHasher:
    """
    Password hashing utility using bcrypt
    
    Bcrypt is industry-standard for password hashing because:
    - It's slow (makes brute-force attacks harder)
    - It automatically handles salt (random data added to password)
    - It's battle-tested and secure
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
            
        Example:
            hashed = PasswordHasher.hash_password("mypassword123")
            # Returns: "$2b$12$abc...xyz" (60 character hash)
        """
        # Convert password to bytes
        password_bytes = password.encode('utf-8')
        
        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=12)  # 12 rounds = good balance of security/speed
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            plain_password: Password entered by user
            hashed_password: Stored hash from database
            
        Returns:
            True if password matches, False otherwise
            
        Example:
            is_valid = PasswordHasher.verify_password("mypassword123", stored_hash)
            if is_valid:
                print("Login successful!")
        """
        try:
            password_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception as e:
            print(f"Password verification error: {e}")
            return False


class TokenManager:
    """
    JWT token management for authentication
    
    JWT tokens contain:
    - User ID (to identify the user)
    - Expiration time (when token becomes invalid)
    - Signature (to prevent tampering)
    """
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Dictionary with user data (usually {"user_id": 123})
            expires_delta: Optional custom expiration time
            
        Returns:
            JWT token string
            
        Example:
            token = TokenManager.create_access_token({"user_id": 42})
            # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        """
        to_encode = data.copy()
        
        # Set expiration time
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow()  # Issued at
        })
        
        # Create token
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token data if valid, None if invalid/expired
            
        Example:
            data = TokenManager.verify_token(token)
            if data:
                user_id = data['user_id']
                print(f"Authenticated user: {user_id}")
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError:
            print("Invalid token")
            return None
    
    @staticmethod
    def decode_token(token: str) -> Optional[int]:
        """
        Extract user ID from token
        
        Args:
            token: JWT token string
            
        Returns:
            User ID if token is valid, None otherwise
        """
        payload = TokenManager.verify_token(token)
        if payload:
            return payload.get("user_id")
        return None


class AuthValidator:
    """
    Validation utilities for authentication
    """
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid email format
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength
        
        Requirements:
        - At least 8 characters
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one number
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        return True, ""
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """
        Validate username format
        
        Requirements:
        - 3-20 characters
        - Alphanumeric and underscore only
        - Must start with a letter
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(username) < 3 or len(username) > 20:
            return False, "Username must be 3-20 characters long"
        
        if not username[0].isalpha():
            return False, "Username must start with a letter"
        
        if not all(c.isalnum() or c == '_' for c in username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, ""


# Example usage
if __name__ == "__main__":
    print("Testing Authentication Utilities\n")
    
    # Test password hashing
    print("1. Password Hashing:")
    password = "MySecurePassword123"
    hashed = PasswordHasher.hash_password(password)
    print(f"   Original: {password}")
    print(f"   Hashed: {hashed}")
    print(f"   Verification: {PasswordHasher.verify_password(password, hashed)}")
    print()
    
    # Test JWT tokens
    print("2. JWT Tokens:")
    token = TokenManager.create_access_token({"user_id": 42, "username": "john_doe"})
    print(f"   Token: {token[:50]}...")
    decoded = TokenManager.verify_token(token)
    print(f"   Decoded: {decoded}")
    print()
    
    # Test validation
    print("3. Validation:")
    print(f"   Email 'test@example.com': {AuthValidator.validate_email('test@example.com')}")
    print(f"   Email 'invalid': {AuthValidator.validate_email('invalid')}")
    valid, msg = AuthValidator.validate_password("Weak")
    print(f"   Password 'Weak': {valid} - {msg}")
    valid, msg = AuthValidator.validate_password("StrongPass123")
    print(f"   Password 'StrongPass123': {valid}")
