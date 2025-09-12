"""
Business Intelligence and Unit Economics models
"""
from sqlalchemy import Column, String, Boolean, JSON, ForeignKey, Enum as SQLEnum, Numeric, DateTime, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
from .base import BaseEntity, AuditMixin

class MetricType(str, Enum):
    """Types of business metrics"""
    COST_PER_CUSTOMER = "cost_per_customer"
    COST_PER_FEATURE = "cost_per_feature"
    COST_PER_TRANSACTION = "cost_per_transaction"
    COST_PER_USER = "cost_per_user"
    COST_PER_REQUEST = "cost_per_request"
    REVENUE_PER_COST = "revenue_per_cost"
    GROSS_MARGIN = "gross_margin"
    CUSTOMER_LIFETIME_VALUE = "customer_lifetime_value"
    CHURN_COST_IMPACT = "churn_cost_impact"

class BusinessEntity(BaseEntity, AuditMixin):
    """Business entities for cost attribution"""
    __tablename__ = "business_entities"
    
    name = Column(String(255), nullable=False)
    entity_type = Column(String(50), nullable=False)  # customer, feature, product, etc.
    external_id = Column(String(255))  # ID from external system
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    # Business attributes
    attributes = Column(JSON, default=dict)  # Flexible attributes
    tags = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    
    # Revenue tracking
    revenue_monthly = Column(Numeric(15, 2))
    revenue_currency = Column(String(3), default="USD")
    
    # Relationships
    organization = relationship("Organization")
    cost_allocations = relationship("CostAllocation", back_populates="business_entity", cascade="all, delete-orphan")
    unit_metrics = relationship("UnitMetric", back_populates="business_entity", cascade="all, delete-orphan")

class CostAllocation(BaseEntity, AuditMixin):
    """Cost allocation to business entities"""
    __tablename__ = "cost_allocations"
    
    # Time dimension
    date = Column(DateTime, nullable=False)
    billing_period = Column(String(7))  # YYYY-MM
    
    # Cost details
    allocated_cost = Column(Numeric(15, 6), nullable=False)
    currency = Column(String(3), default="USD")
    allocation_method = Column(String(50))  # direct, proportional, weighted, etc.
    allocation_weight = Column(Numeric(5, 4), default=1.0)
    
    # References
    business_entity_id = Column(String, ForeignKey("business_entities.id"), nullable=False)
    cost_record_id = Column(String, ForeignKey("cost_records.id"), nullable=True)
    
    # Metadata
    allocation_rules = Column(JSON, default=dict)
    confidence_score = Column(Numeric(3, 2))  # 0.0 to 1.0
    
    # Relationships
    business_entity = relationship("BusinessEntity", back_populates="cost_allocations")

class UnitMetric(BaseEntity, AuditMixin):
    """Unit economics metrics"""
    __tablename__ = "unit_metrics"
    
    # Time dimension
    date = Column(DateTime, nullable=False)
    period_type = Column(String(20), default="daily")  # hourly, daily, weekly, monthly
    
    # Metric details
    metric_type = Column(SQLEnum(MetricType), nullable=False)
    metric_value = Column(Numeric(15, 6), nullable=False)
    unit_count = Column(Numeric(15, 2))  # Number of units (customers, features, etc.)
    
    # Cost breakdown
    infrastructure_cost = Column(Numeric(15, 6))
    operational_cost = Column(Numeric(15, 6))
    allocated_cost = Column(Numeric(15, 6))
    total_cost = Column(Numeric(15, 6))
    
    # Business value
    revenue = Column(Numeric(15, 2))
    gross_margin = Column(Numeric(5, 4))  # Percentage as decimal
    
    # References
    business_entity_id = Column(String, ForeignKey("business_entities.id"), nullable=False)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    # Currency
    currency = Column(String(3), default="USD")
    
    # Metadata
    calculation_method = Column(Text)
    data_sources = Column(JSON, default=list)
    
    # Relationships
    business_entity = relationship("BusinessEntity", back_populates="unit_metrics")
    organization = relationship("Organization")

class BusinessReport(BaseEntity, AuditMixin):
    """Business intelligence reports"""
    __tablename__ = "business_reports"
    
    name = Column(String(255), nullable=False)
    report_type = Column(String(50), nullable=False)  # dashboard, analysis, forecast, etc.
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    # Report configuration
    config = Column(JSON, nullable=False)
    filters = Column(JSON, default=dict)
    schedule = Column(String(50))  # cron expression for scheduled reports
    
    # Report data (cached)
    data = Column(JSON)
    last_generated = Column(DateTime)
    generation_duration = Column(Numeric(8, 3))  # seconds
    
    # Access control
    is_public = Column(Boolean, default=False)
    shared_with = Column(JSON, default=list)  # User/team IDs
    
    # Relationships
    organization = relationship("Organization")

class Forecast(BaseEntity, AuditMixin):
    """Cost and business forecasting"""
    __tablename__ = "forecasts"
    
    name = Column(String(255), nullable=False)
    forecast_type = Column(String(50), nullable=False)  # cost, revenue, units, etc.
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    # Time range
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    forecast_horizon = Column(String(20))  # 1m, 3m, 6m, 1y
    
    # Model details
    model_type = Column(String(50))  # linear, polynomial, arima, ml, etc.
    model_config = Column(JSON, default=dict)
    accuracy_score = Column(Numeric(5, 4))  # 0.0 to 1.0
    
    # Forecast data
    predictions = Column(JSON, nullable=False)
    confidence_intervals = Column(JSON)
    assumptions = Column(JSON, default=dict)
    
    # Metadata
    training_data_period = Column(String(20))  # How much historical data used
    last_trained = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization")

class Anomaly(BaseEntity):
    """Cost and business anomalies"""
    __tablename__ = "anomalies"
    
    # Time and detection
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    anomaly_date = Column(DateTime, nullable=False)
    
    # Anomaly details
    anomaly_type = Column(String(50), nullable=False)  # cost_spike, usage_drop, etc.
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    confidence = Column(Numeric(3, 2), nullable=False)  # 0.0 to 1.0
    
    # Values
    expected_value = Column(Numeric(15, 6))
    actual_value = Column(Numeric(15, 6))
    deviation_percent = Column(Numeric(8, 4))
    
    # Context
    entity_type = Column(String(50))  # account, service, team, project, etc.
    entity_id = Column(String)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    # Investigation
    status = Column(String(20), default="open")  # open, investigating, resolved, false_positive
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    
    # Metadata
    detection_method = Column(String(100))
    alert_sent = Column(Boolean, default=False)
    
    # Relationships
    organization = relationship("Organization")

# Pydantic models for API
class BusinessEntityCreate(BaseModel):
    name: str
    entity_type: str
    external_id: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = {}
    tags: Optional[Dict[str, Any]] = {}
    revenue_monthly: Optional[float] = None
    revenue_currency: str = "USD"

class BusinessEntityResponse(BaseModel):
    id: str
    name: str
    entity_type: str
    external_id: Optional[str]
    is_active: bool
    revenue_monthly: Optional[float]
    attributes: Dict[str, Any]
    tags: Dict[str, Any]
    
    class Config:
        from_attributes = True

class UnitMetricCreate(BaseModel):
    date: datetime
    metric_type: MetricType
    metric_value: float
    unit_count: Optional[float]
    infrastructure_cost: Optional[float]
    operational_cost: Optional[float]
    revenue: Optional[float]
    business_entity_id: str
    calculation_method: Optional[str] = None

class UnitMetricResponse(BaseModel):
    id: str
    date: datetime
    metric_type: MetricType
    metric_value: float
    unit_count: Optional[float]
    total_cost: Optional[float]
    revenue: Optional[float]
    gross_margin: Optional[float]
    business_entity_name: str
    currency: str
    
    class Config:
        from_attributes = True

class BusinessDashboard(BaseModel):
    """Comprehensive business dashboard data"""
    organization_id: str
    period: str
    total_cost: float
    total_revenue: float
    gross_margin: float
    currency: str
    
    # Unit economics
    cost_per_customer: Optional[float]
    revenue_per_customer: Optional[float]
    customer_count: int
    
    # Trends
    cost_trend: List[Dict[str, Any]]
    revenue_trend: List[Dict[str, Any]]
    margin_trend: List[Dict[str, Any]]
    
    # Top insights
    top_cost_drivers: List[Dict[str, Any]]
    efficiency_opportunities: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]

class ForecastCreate(BaseModel):
    name: str
    forecast_type: str
    start_date: datetime
    end_date: datetime
    model_type: str = "linear"
    model_config: Optional[Dict[str, Any]] = {}
    assumptions: Optional[Dict[str, Any]] = {}

class ForecastResponse(BaseModel):
    id: str
    name: str
    forecast_type: str
    start_date: datetime
    end_date: datetime
    accuracy_score: Optional[float]
    predictions: List[Dict[str, Any]]
    confidence_intervals: Optional[List[Dict[str, Any]]]
    last_trained: Optional[datetime]
    
    class Config:
        from_attributes = True