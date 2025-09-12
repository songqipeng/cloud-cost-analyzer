"""
Cloud account and resource models
"""
from sqlalchemy import Column, String, Boolean, JSON, ForeignKey, Enum as SQLEnum, Numeric, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
from .base import BaseEntity, AuditMixin

class CloudProvider(str, Enum):
    """Supported cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ALIBABA = "alibaba"
    TENCENT = "tencent"
    VOLCENGINE = "volcengine"
    ORACLE = "oracle"

class AccountStatus(str, Enum):
    """Cloud account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    SUSPENDED = "suspended"

class ResourceType(str, Enum):
    """Cloud resource types"""
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    CONTAINER = "container"
    SERVERLESS = "serverless"
    AI_ML = "ai_ml"
    OTHER = "other"

class CloudAccount(BaseEntity, AuditMixin):
    """Cloud account model"""
    __tablename__ = "cloud_accounts"
    
    name = Column(String(255), nullable=False)
    provider = Column(SQLEnum(CloudProvider), nullable=False)
    account_id = Column(String(255), nullable=False)  # Cloud provider account ID
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    # Connection details (encrypted)
    credentials = Column(JSON)  # Encrypted credential storage
    regions = Column(JSON, default=list)
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.ACTIVE)
    
    # Metadata
    currency = Column(String(3), default="USD")
    timezone = Column(String(50), default="UTC")
    last_sync = Column(DateTime)
    sync_frequency = Column(String(20), default="daily")  # hourly, daily, weekly
    
    # Settings
    settings = Column(JSON, default=dict)
    tags = Column(JSON, default=dict)
    
    # Relationships
    organization = relationship("Organization", back_populates="cloud_accounts")
    resources = relationship("CloudResource", back_populates="account", cascade="all, delete-orphan")
    cost_records = relationship("CostRecord", back_populates="account", cascade="all, delete-orphan")

class CloudResource(BaseEntity, AuditMixin):
    """Cloud resource model"""
    __tablename__ = "cloud_resources"
    
    resource_id = Column(String(255), nullable=False)  # Cloud provider resource ID
    name = Column(String(500))
    resource_type = Column(SQLEnum(ResourceType), nullable=False)
    service_name = Column(String(100))  # e.g., EC2, RDS, ECS
    region = Column(String(50))
    availability_zone = Column(String(50))
    
    # Resource details
    instance_type = Column(String(100))
    specifications = Column(JSON, default=dict)
    
    # Status and lifecycle
    status = Column(String(50))
    launch_time = Column(DateTime)
    termination_time = Column(DateTime)
    
    # Cost allocation
    account_id = Column(String, ForeignKey("cloud_accounts.id"), nullable=False)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    
    # Metadata
    tags = Column(JSON, default=dict)
    labels = Column(JSON, default=dict)  # Kubernetes labels
    annotations = Column(JSON, default=dict)
    
    # Relationships
    account = relationship("CloudAccount", back_populates="resources")
    cost_records = relationship("CostRecord", back_populates="resource", cascade="all, delete-orphan")

class CostRecord(BaseEntity):
    """Cost record model for tracking expenses"""
    __tablename__ = "cost_records"
    
    # Time dimensions
    date = Column(DateTime, nullable=False)
    billing_period = Column(String(7))  # YYYY-MM format
    
    # Resource identification
    account_id = Column(String, ForeignKey("cloud_accounts.id"), nullable=False)
    resource_id = Column(String, ForeignKey("cloud_resources.id"), nullable=True)
    service_name = Column(String(100))
    usage_type = Column(String(200))
    operation = Column(String(200))
    
    # Cost details
    cost = Column(Numeric(15, 6), nullable=False)
    currency = Column(String(3), default="USD")
    usage_quantity = Column(Numeric(15, 6))
    usage_unit = Column(String(50))
    
    # Allocation
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    cost_center = Column(String(100))
    
    # Metadata
    tags = Column(JSON, default=dict)
    dimensions = Column(JSON, default=dict)  # Additional cost dimensions
    
    # Relationships
    account = relationship("CloudAccount", back_populates="cost_records")
    resource = relationship("CloudResource", back_populates="cost_records")

# Pydantic models for API
class CloudAccountCreate(BaseModel):
    name: str
    provider: CloudProvider
    account_id: str
    credentials: Dict[str, Any]
    regions: Optional[List[str]] = []
    currency: str = "USD"
    timezone: str = "UTC"
    sync_frequency: str = "daily"
    settings: Optional[Dict[str, Any]] = {}
    tags: Optional[Dict[str, Any]] = {}

class CloudAccountResponse(BaseModel):
    id: str
    name: str
    provider: CloudProvider
    account_id: str
    status: AccountStatus
    currency: str
    timezone: str
    last_sync: Optional[datetime]
    resource_count: int
    monthly_cost: Optional[float]
    
    class Config:
        from_attributes = True

class CloudResourceResponse(BaseModel):
    id: str
    resource_id: str
    name: Optional[str]
    resource_type: ResourceType
    service_name: str
    region: str
    instance_type: Optional[str]
    status: str
    launch_time: Optional[datetime]
    monthly_cost: Optional[float]
    tags: Dict[str, Any]
    
    class Config:
        from_attributes = True

class CostRecordCreate(BaseModel):
    date: datetime
    service_name: str
    cost: float
    currency: str = "USD"
    usage_quantity: Optional[float]
    usage_unit: Optional[str]
    project_id: Optional[str]
    team_id: Optional[str]
    tags: Optional[Dict[str, Any]] = {}

class CostRecordResponse(BaseModel):
    id: str
    date: datetime
    service_name: str
    cost: float
    currency: str
    usage_quantity: Optional[float]
    usage_unit: Optional[str]
    project_name: Optional[str]
    team_name: Optional[str]
    
    class Config:
        from_attributes = True

class CostSummary(BaseModel):
    """Cost summary for dashboards"""
    total_cost: float
    currency: str
    period: str
    cost_by_service: Dict[str, float]
    cost_by_team: Dict[str, float]
    cost_by_project: Dict[str, float]
    cost_trend: List[Dict[str, Any]]