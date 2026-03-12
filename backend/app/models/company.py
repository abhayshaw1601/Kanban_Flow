"""
Company model for multi-tenant support.

This model represents companies/organizations in the system.
Each user belongs to a company, and users can only see other users
from their own company.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..core.database import Base


class Company(Base):
    """
    Company model for multi-tenant support.
    
    Attributes:
        id: Primary key
        name: Company name
        company_id: Unique company identifier (user-friendly)
        description: Optional company description
        created_at: Timestamp when company was created
        
    Relationships:
        users: All users belonging to this company
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    company_id = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users = relationship("User", back_populates="company")