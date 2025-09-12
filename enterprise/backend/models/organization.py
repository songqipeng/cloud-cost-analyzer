"""
Organization and user management models
"""
from sqlalchemy import Column, String, Boolean, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any, List
from enum import Enum
from .base import BaseEntity, AuditMixin

class UserRole(str, Enum):
    """User roles in the system"""
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    FINANCE_MANAGER = "finance_manager"
    TEAM_LEAD = "team_lead"
    DEVELOPER = "developer"
    VIEWER = "viewer"

class SubscriptionTier(str, Enum):
    """Subscription tiers"""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class Organization(BaseEntity, AuditMixin):
    """Organization model"""
    __tablename__ = "organizations"
    
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=True)
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.STARTER)
    settings = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="organization", cascade="all, delete-orphan")
    cloud_accounts = relationship("CloudAccount", back_populates="organization", cascade="all, delete-orphan")

class Team(BaseEntity, AuditMixin):
    """Team model"""
    __tablename__ = "teams"
    
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    cost_center = Column(String(100))
    budget_monthly = Column(String)  # Using String to handle different currencies
    settings = Column(JSON, default=dict)
    
    # Relationships
    organization = relationship("Organization", back_populates="teams")
    members = relationship("User", back_populates="team")
    projects = relationship("Project", back_populates="team", cascade="all, delete-orphan")

class User(BaseEntity, AuditMixin):
    """User model"""
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    last_login = Column(String)
    preferences = Column(JSON, default=dict)
    
    # Foreign keys
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    team = relationship("Team", back_populates="members")

class Project(BaseEntity, AuditMixin):
    """Project model for cost tracking"""
    __tablename__ = "projects"
    
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    team_id = Column(String, ForeignKey("teams.id"), nullable=False)
    cost_center = Column(String(100))
    budget_monthly = Column(String)
    tags = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    team = relationship("Team", back_populates="projects")

# Pydantic models for API
class OrganizationCreate(BaseModel):
    name: str
    domain: Optional[str] = None
    subscription_tier: SubscriptionTier = SubscriptionTier.STARTER
    settings: Optional[Dict[str, Any]] = {}

class OrganizationResponse(BaseModel):
    id: str
    name: str
    domain: Optional[str]
    subscription_tier: SubscriptionTier
    is_active: bool
    user_count: int
    team_count: int
    
    class Config:
        from_attributes = True

class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None
    cost_center: Optional[str] = None
    budget_monthly: Optional[str] = None
    settings: Optional[Dict[str, Any]] = {}

class TeamResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    cost_center: Optional[str]
    budget_monthly: Optional[str]
    member_count: int
    project_count: int
    
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    role: UserRole = UserRole.VIEWER
    team_id: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = {}

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    is_active: bool
    team_name: Optional[str]
    last_login: Optional[str]
    
    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    team_id: str
    cost_center: Optional[str] = None
    budget_monthly: Optional[str] = None
    tags: Optional[Dict[str, Any]] = {}

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    team_name: str
    cost_center: Optional[str]
    budget_monthly: Optional[str]
    is_active: bool
    tags: Dict[str, Any]
    
    class Config:
        from_attributes = True