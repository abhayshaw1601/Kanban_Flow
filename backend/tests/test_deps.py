"""
Tests for authentication and authorization dependencies.

Tests the get_current_user and get_current_admin dependencies to ensure:
- JWT tokens are properly validated
- Users are correctly retrieved from the database
- Admin role checks work correctly
- Appropriate errors are raised for invalid tokens or insufficient permissions
"""

import pytest
from fastapi import HTTPException

from app.core.deps import get_current_user, get_current_admin
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User, UserRole


class TestGetCurrentUser:
    """Test get_current_user dependency."""
    
    @pytest.mark.asyncio
    async def test_missing_token_raises_401(self):
        """Test that get_current_user raises 401 when token is missing."""
        # Mock database session (won't be used since we fail before DB query)
        mock_db = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(access_token=None, db=mock_db)
        
        assert exc_info.value.status_code == 401
        assert "Not authenticated" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_invalid_token_raises_401(self):
        """Test that get_current_user raises 401 with invalid token."""
        invalid_token = "invalid.jwt.token"
        mock_db = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(access_token=invalid_token, db=mock_db)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_refresh_token_rejected(self):
        """Test that get_current_user rejects refresh tokens (only accepts access tokens)."""
        # Create a refresh token instead of access token (sub must be string)
        refresh_token = create_refresh_token({"sub": "123"})
        mock_db = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(access_token=refresh_token, db=mock_db)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token type" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_token_without_user_id_raises_401(self):
        """Test that token without 'sub' claim raises 401."""
        # Create token without user ID
        token = create_access_token({"email": "test@example.com"})
        mock_db = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(access_token=token, db=mock_db)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token: missing user ID" in exc_info.value.detail


class TestGetCurrentAdmin:
    """Test get_current_admin dependency."""
    
    @pytest.mark.asyncio
    async def test_admin_user_allowed(self):
        """Test that get_current_admin allows admin users."""
        # Create a mock admin user
        admin_user = User(
            id=1,
            name="Admin User",
            email="admin@test.com",
            password="hashed",
            role=UserRole.ADMIN
        )
        
        # Call the dependency with an admin user
        result = await get_current_admin(current_user=admin_user)
        
        # Verify the admin user is returned
        assert result.id == admin_user.id
        assert result.role == UserRole.ADMIN
    
    @pytest.mark.asyncio
    async def test_employee_user_rejected(self):
        """Test that get_current_admin rejects employee users with 403."""
        # Create a mock employee user
        employee_user = User(
            id=2,
            name="Employee User",
            email="employee@test.com",
            password="hashed",
            role=UserRole.EMPLOYEE
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await get_current_admin(current_user=employee_user)
        
        assert exc_info.value.status_code == 403
        assert "Admin access required" in exc_info.value.detail


class TestAuthenticationFlow:
    """Test complete authentication flow scenarios."""
    
    def test_valid_access_token_structure(self):
        """Test that created access tokens have correct structure."""
        user_id = "123"  # JWT sub claim must be a string
        token = create_access_token({"sub": user_id})
        
        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Should be able to decode it
        from app.core.security import decode_token
        payload = decode_token(token)
        
        # Should have correct claims
        assert payload["sub"] == user_id
        assert payload["type"] == "access"
        assert "exp" in payload
    
    def test_token_type_validation(self):
        """Test that token type is properly validated."""
        # Access token should have type "access" (sub must be string)
        access_token = create_access_token({"sub": "1"})
        from app.core.security import decode_token
        access_payload = decode_token(access_token)
        assert access_payload["type"] == "access"
        
        # Refresh token should have type "refresh"
        refresh_token = create_refresh_token({"sub": "1"})
        refresh_payload = decode_token(refresh_token)
        assert refresh_payload["type"] == "refresh"
