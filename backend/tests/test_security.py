"""
Unit tests for security utilities (password hashing and JWT tokens).

Tests cover:
- Password hashing with bcrypt
- Password verification
- Access token creation and validation
- Refresh token creation and validation
- Token decoding
- Token expiry validation
"""

import pytest
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.core.config import settings


class TestPasswordHashing:
    """Test password hashing and verification functions."""
    
    def test_get_password_hash_returns_bcrypt_hash(self):
        """Test that get_password_hash returns a valid bcrypt hash."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Bcrypt hashes start with $2b$
        assert hashed.startswith("$2b$")
        # Hash should not be the same as plaintext
        assert hashed != password
        # Hash should be a reasonable length (bcrypt hashes are 60 chars)
        assert len(hashed) == 60
    
    def test_get_password_hash_different_for_same_password(self):
        """Test that hashing the same password twice produces different hashes (due to salt)."""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to random salt
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    def test_verify_password_correct_password(self):
        """Test that verify_password returns True for correct password."""
        password = "mypassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        password = "mypassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty_password(self):
        """Test password verification with empty password."""
        password = "mypassword123"
        hashed = get_password_hash(password)
        
        assert verify_password("", hashed) is False
    
    def test_password_hash_special_characters(self):
        """Test password hashing with special characters."""
        password = "P@ssw0rd!#$%^&*()"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("P@ssw0rd", hashed) is False


class TestAccessToken:
    """Test access token creation and validation."""
    
    def test_create_access_token_basic(self):
        """Test creating a basic access token."""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_contains_subject(self):
        """Test that access token contains the subject claim."""
        user_id = "456"
        data = {"sub": user_id}
        token = create_access_token(data)
        
        payload = decode_token(token)
        assert payload["sub"] == user_id
    
    def test_create_access_token_has_type(self):
        """Test that access token has type 'access'."""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        payload = decode_token(token)
        assert payload["type"] == "access"
    
    def test_create_access_token_has_expiry(self):
        """Test that access token has expiry time set correctly."""
        data = {"sub": "123"}
        before_creation = datetime.utcnow()
        token = create_access_token(data)
        after_creation = datetime.utcnow()
        
        payload = decode_token(token)
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
        
        # Expiry should be approximately 30 minutes from now
        expected_expiry = before_creation + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        time_diff = abs((exp_datetime - expected_expiry).total_seconds())
        
        # Allow 5 seconds tolerance for test execution time
        assert time_diff < 5
    
    def test_create_access_token_with_additional_claims(self):
        """Test creating access token with additional claims."""
        data = {"sub": "123", "email": "test@example.com", "role": "admin"}
        token = create_access_token(data)
        
        payload = decode_token(token)
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "admin"
        assert payload["type"] == "access"


class TestRefreshToken:
    """Test refresh token creation and validation."""
    
    def test_create_refresh_token_basic(self):
        """Test creating a basic refresh token."""
        data = {"sub": "123"}
        token = create_refresh_token(data)
        
        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_refresh_token_contains_subject(self):
        """Test that refresh token contains the subject claim."""
        user_id = "789"
        data = {"sub": user_id}
        token = create_refresh_token(data)
        
        payload = decode_token(token)
        assert payload["sub"] == user_id
    
    def test_create_refresh_token_has_type(self):
        """Test that refresh token has type 'refresh'."""
        data = {"sub": "123"}
        token = create_refresh_token(data)
        
        payload = decode_token(token)
        assert payload["type"] == "refresh"
    
    def test_create_refresh_token_has_expiry(self):
        """Test that refresh token has expiry time set correctly."""
        data = {"sub": "123"}
        before_creation = datetime.utcnow()
        token = create_refresh_token(data)
        after_creation = datetime.utcnow()
        
        payload = decode_token(token)
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
        
        # Expiry should be approximately 7 days from now
        expected_expiry = before_creation + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        time_diff = abs((exp_datetime - expected_expiry).total_seconds())
        
        # Allow 5 seconds tolerance for test execution time
        assert time_diff < 5
    
    def test_refresh_token_longer_expiry_than_access(self):
        """Test that refresh token has longer expiry than access token."""
        data = {"sub": "123"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)
        
        # Refresh token should expire after access token
        assert refresh_payload["exp"] > access_payload["exp"]


class TestDecodeToken:
    """Test token decoding and validation."""
    
    def test_decode_token_valid_access_token(self):
        """Test decoding a valid access token."""
        data = {"sub": "123", "email": "test@example.com"}
        token = create_access_token(data)
        
        payload = decode_token(token)
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["type"] == "access"
        assert "exp" in payload
    
    def test_decode_token_valid_refresh_token(self):
        """Test decoding a valid refresh token."""
        data = {"sub": "456"}
        token = create_refresh_token(data)
        
        payload = decode_token(token)
        assert payload["sub"] == "456"
        assert payload["type"] == "refresh"
        assert "exp" in payload
    
    def test_decode_token_invalid_token(self):
        """Test that decoding an invalid token raises JWTError."""
        invalid_token = "invalid.token.string"
        
        with pytest.raises(JWTError):
            decode_token(invalid_token)
    
    def test_decode_token_tampered_token(self):
        """Test that decoding a tampered token raises JWTError."""
        data = {"sub": 123}
        token = create_access_token(data)
        
        # Tamper with the token by changing a character
        tampered_token = token[:-5] + "XXXXX"
        
        with pytest.raises(JWTError):
            decode_token(tampered_token)
    
    def test_decode_token_wrong_secret(self):
        """Test that token signed with different secret cannot be decoded."""
        # Create token with different secret
        data = {"sub": 123}
        wrong_secret_token = jwt.encode(
            data,
            "wrong-secret-key",
            algorithm=settings.ALGORITHM
        )
        
        with pytest.raises(JWTError):
            decode_token(wrong_secret_token)
    
    def test_decode_token_expired_token(self):
        """Test that decoding an expired token raises JWTError."""
        # Create token that expired 1 hour ago
        data = {"sub": "123"}
        past_time = datetime.utcnow() - timedelta(hours=1)
        expired_data = {
            **data,
            "exp": past_time,
            "type": "access"
        }
        expired_token = jwt.encode(
            expired_data,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        with pytest.raises(JWTError):
            decode_token(expired_token)


class TestTokenRoundTrip:
    """Test complete token creation and validation workflows."""
    
    def test_access_token_round_trip(self):
        """Test creating and decoding an access token."""
        original_data = {"sub": "999", "email": "user@example.com", "role": "employee"}
        
        # Create token
        token = create_access_token(original_data)
        
        # Decode token
        decoded_data = decode_token(token)
        
        # Verify all original data is present
        assert decoded_data["sub"] == original_data["sub"]
        assert decoded_data["email"] == original_data["email"]
        assert decoded_data["role"] == original_data["role"]
        assert decoded_data["type"] == "access"
    
    def test_refresh_token_round_trip(self):
        """Test creating and decoding a refresh token."""
        original_data = {"sub": "888"}
        
        # Create token
        token = create_refresh_token(original_data)
        
        # Decode token
        decoded_data = decode_token(token)
        
        # Verify data
        assert decoded_data["sub"] == original_data["sub"]
        assert decoded_data["type"] == "refresh"
    
    def test_token_types_are_distinguishable(self):
        """Test that access and refresh tokens can be distinguished by type."""
        data = {"sub": "123"}
        
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)
        
        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)
        
        assert access_payload["type"] == "access"
        assert refresh_payload["type"] == "refresh"
        assert access_payload["type"] != refresh_payload["type"]
