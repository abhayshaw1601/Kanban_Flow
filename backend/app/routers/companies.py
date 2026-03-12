"""
Company management API endpoints.

This module provides endpoints for managing companies in the multi-tenant system.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.deps import get_current_user
from ..models.user import User
from ..models.company import Company
from ..schemas.company import CompanyResponse, CompanySelect


router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("", response_model=List[CompanySelect])
async def get_companies(
    db: Session = Depends(get_db)
):
    """
    Get all companies for selection during registration.
    
    This endpoint returns a list of all companies that users can join during registration.
    No authentication required as this is used during the signup process.
    
    Args:
        db: Database session
        
    Returns:
        List[CompanySelect]: List of companies with basic info for selection
    """
    companies = db.query(Company).all()
    return companies


@router.get("/my-company", response_model=CompanyResponse)
async def get_my_company(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the current user's company information.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        CompanyResponse: Company information
        
    Raises:
        HTTPException 404: If company not found
    """
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company