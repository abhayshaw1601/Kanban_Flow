"""
Security utilities for password hashing and JWT token management.

This module provides functions for:
- Password hashing using bcrypt
- Password verification
- JWT access token creation (30 min expiry)
- JWT refresh token creation (7 day expiry)
- JWT token decoding and validation
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from jose import JWTError, jwt
import bcrypt
from .config import settings


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Bcrypt hashed password string
        
    Example:
        >>> hashed = get_password_hash("mypassword123")
        >>> hashed.startswith("$2b$")
        True
    """
    # Convert password to bytes and hash with bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a bcrypt hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
        
    Example:
        >>> hashed = get_password_hash("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    # Convert both to bytes for bcrypt
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT access token with 30 minute expiry.
    
    Args:
        data: Dictionary of claims to encode in the token (typically {"sub": user_id})
        
    Returns:
        Encoded JWT token string
        
    Example:
        >>> token = create_access_token({"sub": 123})
        >>> payload = decode_token(token)
        >>> payload["sub"]
        123
        >>> payload["type"]
        'access'
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token with 7 day expiry.
    
    Args:
        data: Dictionary of claims to encode in the token (typically {"sub": user_id})
        
    Returns:
        Encoded JWT token string
        
    Example:
        >>> token = create_refresh_token({"sub": 123})
        >>> payload = decode_token(token)
        >>> payload["sub"]
        123
        >>> payload["type"]
        'refresh'
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Dictionary containing the token payload
        
    Raises:
        JWTError: If token is invalid, expired, or signature doesn't match
        
    Example:
        >>> token = create_access_token({"sub": 123})
        >>> payload = decode_token(token)
        >>> payload["sub"]
        123
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return payload
