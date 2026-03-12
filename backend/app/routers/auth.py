"""
Authentication API routes for user registration, login, logout, and token refresh.

This module provides endpoints for:
- POST /api/auth/register - User registration
- POST /api/auth/login - User login
- POST /api/auth/refresh - Token refresh
- POST /api/auth/logout - User logout
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jose import JWTError
from typing import Optional

from ..core.database import get_db
from ..core.config import settings
from ..core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from ..models.user import User, UserRole
from ..models.company import Company
from ..schemas.auth import LoginRequest, TokenResponse
from ..schemas.user import UserCreate, UserResponse


router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account with company selection or creation.
    
    Creates a new user with:
    - Bcrypt hashed password (never stored as plaintext)
    - Selected role (admin or employee)
    - Company association (existing or new)
    - Unique email validation
    - Timestamp for account creation
    
    Args:
        user_data: User registration data (name, email, password, role, company info)
        db: Database session dependency
        
    Returns:
        UserResponse: Created user data (excluding password)
        
    Raises:
        HTTPException 400: If email already exists or validation fails
        
    Validates: Requirements 1.1, 24.1
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role
    if user_data.role not in ["admin", "employee"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role must be 'admin' or 'employee'"
        )
    
    # Handle company selection or creation
    company_id = None
    
    if user_data.company_id:
        # User selected existing company
        company = db.query(Company).filter(Company.id == user_data.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected company not found"
            )
        company_id = company.id
    else:
        # User wants to create new company
        if not user_data.company_name or not user_data.company_identifier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company name and identifier are required for new company"
            )
        
        # Check if company identifier already exists
        existing_company = db.query(Company).filter(
            Company.company_id == user_data.company_identifier
        ).first()
        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company identifier already exists"
            )
        
        # Create new company
        new_company = Company(
            name=user_data.company_name,
            company_id=user_data.company_identifier,
            description=user_data.company_description
        )
        db.add(new_company)
        db.flush()  # Get the company ID
        company_id = new_company.id
    
    # Hash the password using bcrypt
    hashed_password = get_password_hash(user_data.password)
    
    # Create new user with specified role
    user_role = UserRole.ADMIN if user_data.role == "admin" else UserRole.EMPLOYEE
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        role=user_role,
        company_id=company_id
    )
    
    try:
        # Add user to database
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        # Handle race condition where email was added between check and insert
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Return user data (password excluded by UserResponse schema)
    return new_user


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and issue JWT tokens.
    
    Validates credentials and generates:
    - Access token (30 min expiry) - for API authentication
    - Refresh token (7 day expiry) - for obtaining new access tokens
    
    Both tokens are set as httpOnly cookies for security (prevents XSS attacks).
    
    Args:
        response: FastAPI Response object for setting cookies
        credentials: Login credentials (email and password)
        db: Database session dependency
        
    Returns:
        dict: Success message with user information
        
    Raises:
        HTTPException 401: If credentials are invalid
        
    Validates: Requirements 1.2, 24.2, 29.3
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    # Validate user exists and password is correct
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate JWT tokens with user ID as subject (must be string for JWT spec)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Set tokens as httpOnly cookies (secure, cannot be accessed via JavaScript)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,  # Only send over HTTPS in production
        samesite="lax",  # CSRF protection
        max_age=30 * 60  # 30 minutes in seconds
    )
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=7 * 24 * 60 * 60  # 7 days in seconds
    )
    
    # Return success response with user info (password excluded)
    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value,
            "avatar": user.avatar
        }
    }


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token.
    
    Validates the refresh token from httpOnly cookie and issues a new access token.
    This allows users to maintain their session without re-authenticating when
    the access token expires (after 30 minutes).
    
    Args:
        response: FastAPI Response object for setting cookies
        refresh_token: Refresh token from httpOnly cookie
        db: Database session dependency
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException 401: If refresh token is missing, invalid, or expired
        HTTPException 404: If user no longer exists
        
    Validates: Requirements 1.3, 24.3
    """
    # Check if refresh token is provided
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not provided"
        )
    
    try:
        # Decode and validate the refresh token
        payload = decode_token(refresh_token)
        
        # Verify this is a refresh token (not an access token)
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Extract user ID from token
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Convert user ID to integer
        user_id = int(user_id_str)
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    
    # Verify user still exists in database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Generate new access token
    new_access_token = create_access_token(data={"sub": str(user.id)})
    
    # Set new access token as httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,  # Only send over HTTPS in production
        samesite="lax",  # CSRF protection
        max_age=30 * 60  # 30 minutes in seconds
    )
    
    # Return success response
    return {
        "message": "Access token refreshed successfully"
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(response: Response):
    """
    Logout user by clearing authentication tokens.
    
    Invalidates the user session by clearing both access_token and refresh_token
    httpOnly cookies. This prevents the tokens from being sent in future requests,
    effectively logging the user out.
    
    Args:
        response: FastAPI Response object for clearing cookies
        
    Returns:
        dict: Success message
        
    Validates: Requirements 1.4, 24.4
    """
    # Clear access_token cookie by setting max_age to 0
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    # Clear refresh_token cookie by setting max_age to 0
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    
    # Return success response
    return {
        "message": "Logout successful"
    }
