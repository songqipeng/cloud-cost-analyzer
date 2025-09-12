"""
Base models and database configuration for Enterprise Cloud Cost Analyzer
"""
from datetime import datetime
from typing import Optional, Any, Dict
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel
import uuid

Base = declarative_base()

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

class BaseEntity(Base, TimestampMixin, SoftDeleteMixin):
    """Base entity with common fields"""
    __abstract__ = True
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
class AuditMixin:
    """Mixin for audit trail"""
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    version = Column(Integer, default=1, nullable=False)

# Pydantic base models for API
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = datetime.utcnow()

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = 1
    size: int = 20
    sort_by: Optional[str] = "created_at"
    sort_order: str = "desc"

class PaginatedResponse(BaseResponse):
    """Paginated response model"""
    data: list
    total: int
    page: int
    size: int
    pages: int