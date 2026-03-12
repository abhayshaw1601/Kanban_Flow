"""
Company Pydantic schemas for request/response validation.

These schemas define the structure for company-related API requests and responses,
supporting multi-tenant functionality.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class CompanyCreate(BaseModel):
    """
    Schema for company creation requests.
    
    Validates:
        - name: Required, non-empty string
        - company_id: Required, unique identifier
        - description: Optional string
    """
    name: str = Field(..., min_length=1, max_length=200, description="Company name")
    company_id: str = Field(..., min_length=1, max_length=50, description="Unique company identifier")
    description: Optional[str] = Field(None, max_length=1000, description="Company description")


class CompanyResponse(BaseModel):
    """
    Schema for company data in API responses.
    
    Includes all company information.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    company_id: str
    description: Optional[str] = None
    created_at: datetime


class CompanySelect(BaseModel):
    """
    Schema for company selection during registration.
    
    Used when users need to select or create a company.
    """
    id: int
    name: str
    company_id: str
    description: Optional[str] = None