"""
Security utilities for FitLog.
- Password hashing with PBKDF2  
- JWT token generation and validation
- Role-based access control
"""
import os
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets

from jose import JWTError, jwt

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours


def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2 (compatible with all platforms).
    Format: algorithm$iterations$salt$hash
    """
    iterations = 100000
    salt = secrets.token_hex(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt.encode(),
        iterations
    )
    return f"pbkdf2_sha256${iterations}${salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        algorithm, iterations, salt, stored_hash = hashed_password.split('$')
        
        if algorithm != "pbkdf2_sha256":
            return False
            
        key = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode(),
            salt.encode(),
            int(iterations)
        )
        return key.hex() == stored_hash
    except (ValueError, AttributeError):
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
