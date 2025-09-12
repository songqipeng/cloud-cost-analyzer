"""
Automated Cloud Cost Optimization Engine
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import math
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.cloud_account import CloudResource, CostRecord
from ..models.optimization import OptimizationRecommendation, OptimizationRule, OptimizationAction
from ..utils.cloud_providers import get_cloud_provider_client
from ..utils.notifications import send_notification

logger = logging.getLogger(__name__)

class OptimizationType(str, Enum):
    """Types of optimization recommendations"""
    RIGHTSIZING = "rightsizing"
    RESERVED_INSTANCES = "reserved_instances"
    SPOT_INSTANCES = "spot_instances"
    IDLE_RESOURCES = "idle_resources"
    STORAGE_OPTIMIZATION = "storage_optimization"
    SCHEDULED_SCALING = "scheduled_scaling"
    COMMITMENT_PLANNING = "commitment_planning"
    RESOURCE_TAGGING = "resource_tagging"

class Priority(str, Enum):
    """Priority levels for optimization recommendations"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class OptimizationOpportunity:
    """Represents an optimization opportunity"""
    resource_id: str
    resource_name: str
    optimization_type: OptimizationType
    priority: Priority
    current_cost: float
    potential_savings: float
    savings_percentage: float
    confidence_score: float
    implementation_effort: str
    risk_level: str
    description: str
    action_steps: List[str]
    metadata: Dict[str, Any]

class OptimizationEngine:
    """Main optimization engine for automated cost optimization"""
    
    def __init__(self, db: Session):
        self.db = db
        self.rules = self._load_optimization_rules()
        
    def _load_optimization_rules(self) -> List[OptimizationRule]:
        """Load optimization rules from database"""
        return self.db.query(OptimizationRule).filter(
            OptimizationRule.is_active == True
        ).all()
    
    async def analyze_optimization_opportunities(
        self, 
        organization_id: str,
        cloud_account_ids: Optional[List[str]] = None,
        optimization_types: Optional[List[OptimizationType]] = None
    ) -> List[OptimizationOpportunity]:
        """Analyze and identify optimization opportunities"""
        logger.info(f"Starting optimization analysis for organization {organization_id}")
        
        opportunities = []
        
        # Get resources to analyze
        resources = self._get_resources_for_analysis(organization_id, cloud_account_ids)
        
        # Run different optimization analyses in parallel
        tasks = []
        
        if not optimization_types or OptimizationType.RIGHTSIZING in optimization_types:
            tasks.append(self._analyze_rightsizing_opportunities(resources))
            
        if not optimization_types or OptimizationType.IDLE_RESOURCES in optimization_types:
            tasks.append(self._analyze_idle_resources(resources))
            
        if not optimization_types or OptimizationType.RESERVED_INSTANCES in optimization_types:
            tasks.append(self._analyze_reserved_instance_opportunities(resources))
            
        if not optimization_types or OptimizationType.SPOT_INSTANCES in optimization_types:
            tasks.append(self._analyze_spot_instance_opportunities(resources))
            
        if not optimization_types or OptimizationType.STORAGE_OPTIMIZATION in optimization_types:
            tasks.append(self._analyze_storage_optimization(resources))
            
        if not optimization_types or OptimizationType.SCHEDULED_SCALING in optimization_types:
            tasks.append(self._analyze_scheduled_scaling_opportunities(resources))
        
        # Execute all analyses concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Optimization analysis failed: {result}")
                continue
            opportunities.extend(result)
        
        # Sort by potential savings (highest first)
        opportunities.sort(key=lambda x: x.potential_savings, reverse=True)
        
        logger.info(f"Found {len(opportunities)} optimization opportunities")
        return opportunities
    
    def _get_resources_for_analysis(
        self, 
        organization_id: str, 
        cloud_account_ids: Optional[List[str]]
    ) -> List[CloudResource]:
        """Get cloud resources for optimization analysis"""
        query = self.db.query(CloudResource).join(CloudResource.account).filter(
            CloudResource.account.has(organization_id=organization_id),
            CloudResource.is_deleted == False
        )
        
        if cloud_account_ids:
            query = query.filter(CloudResource.account_id.in_(cloud_account_ids))
        
        return query.all()
    
    async def _analyze_rightsizing_opportunities(
        self, 
        resources: List[CloudResource]
    ) -> List[OptimizationOpportunity]:
        """Analyze rightsizing opportunities for compute resources"""
        opportunities = []
        
        # Filter compute resources
        compute_resources = [r for r in resources if r.resource_type == "compute"]
        
        for resource in compute_resources:
            try:
                # Get utilization metrics
                utilization = await self._get_resource_utilization(resource)
                cost_data = await self._get_resource_cost_data(resource)
                
                if not utilization or not cost_data:
                    continue
                
                # Analyze CPU utilization
                avg_cpu = utilization.get('avg_cpu_utilization', 0)
                max_cpu = utilization.get('max_cpu_utilization', 0)
                avg_memory = utilization.get('avg_memory_utilization', 0)
                
                # Rightsizing logic
                if avg_cpu < 20 and max_cpu < 50:  # Under-utilized
                    recommendation = await self._generate_downsize_recommendation(
                        resource, utilization, cost_data
                    )
                    if recommendation:
                        opportunities.append(recommendation)
                        
                elif avg_cpu > 80 or max_cpu > 95:  # Over-utilized
                    recommendation = await self._generate_upsize_recommendation(
                        resource, utilization, cost_data
                    )
                    if recommendation:
                        opportunities.append(recommendation)
                
            except Exception as e:
                logger.error(f"Failed to analyze rightsizing for {resource.resource_id}: {e}")
                continue
        
        return opportunities
    
    async def _analyze_idle_resources(
        self, 
        resources: List[CloudResource]
    ) -> List[OptimizationOpportunity]:
        """Identify idle or unused resources"""
        opportunities = []
        
        for resource in resources:
            try:
                # Check if resource is idle
                is_idle, idle_metrics = await self._check_resource_idle(resource)
                
                if is_idle:
                    cost_data = await self._get_resource_cost_data(resource)
                    monthly_cost = cost_data.get('monthly_cost', 0)
                    
                    opportunity = OptimizationOpportunity(
                        resource_id=resource.resource_id,
                        resource_name=resource.name or resource.resource_id,
                        optimization_type=OptimizationType.IDLE_RESOURCES,
                        priority=Priority.HIGH if monthly_cost > 500 else Priority.MEDIUM,
                        current_cost=monthly_cost,
                        potential_savings=monthly_cost * 0.95,  # Almost full savings
                        savings_percentage=95.0,
                        confidence_score=idle_metrics.get('confidence', 0.8),
                        implementation_effort="Low",
                        risk_level="Low",
                        description=f"Resource appears to be idle with {idle_metrics.get('idle_days', 0)} days of no activity",
                        action_steps=[
                            "Verify resource is not needed",
                            "Create snapshot/backup if necessary",
                            "Terminate or stop the resource",
                            "Monitor for any alerts or issues"
                        ],
                        metadata={
                            "idle_days": idle_metrics.get('idle_days', 0),
                            "last_activity": idle_metrics.get('last_activity'),
                            "resource_type": resource.resource_type,
                            "service_name": resource.service_name
                        }
                    )
                    opportunities.append(opportunity)
                    
            except Exception as e:
                logger.error(f"Failed to analyze idle resource {resource.resource_id}: {e}")
                continue
        
        return opportunities
    
    async def _analyze_reserved_instance_opportunities(
        self, 
        resources: List[CloudResource]
    ) -> List[OptimizationOpportunity]:
        """Analyze Reserved Instance/Committed Use opportunities"""
        opportunities = []
        
        # Group resources by instance type and region
        instance_groups = {}
        for resource in resources:
            if resource.resource_type == "compute" and resource.instance_type:
                key = (resource.instance_type, resource.region)
                if key not in instance_groups:
                    instance_groups[key] = []
                instance_groups[key].append(resource)
        
        for (instance_type, region), group_resources in instance_groups.items():
            try:
                # Analyze usage patterns
                stable_instances = []
                for resource in group_resources:
                    uptime_days = await self._get_resource_uptime_days(resource)
                    if uptime_days >= 30:  # Running for at least 30 days
                        stable_instances.append(resource)
                
                if len(stable_instances) >= 1:  # At least one stable instance
                    # Calculate potential RI savings
                    total_monthly_cost = sum([
                        (await self._get_resource_cost_data(r)).get('monthly_cost', 0)
                        for r in stable_instances
                    ])
                    
                    # Typical RI savings: 30-60% depending on commitment
                    ri_savings_percentage = 45.0  # Average savings
                    potential_savings = total_monthly_cost * (ri_savings_percentage / 100)
                    
                    if potential_savings > 100:  # Only recommend if savings > $100/month
                        opportunity = OptimizationOpportunity(
                            resource_id=f"RI-{instance_type}-{region}",
                            resource_name=f"Reserved Instances for {instance_type} in {region}",
                            optimization_type=OptimizationType.RESERVED_INSTANCES,
                            priority=Priority.HIGH if potential_savings > 1000 else Priority.MEDIUM,
                            current_cost=total_monthly_cost,
                            potential_savings=potential_savings,
                            savings_percentage=ri_savings_percentage,
                            confidence_score=0.9,
                            implementation_effort="Medium",
                            risk_level="Low",
                            description=f"Purchase Reserved Instances for {len(stable_instances)} stable {instance_type} instances",
                            action_steps=[
                                "Analyze historical usage patterns",
                                "Choose appropriate RI term (1 or 3 years)",
                                "Purchase Reserved Instances",
                                "Monitor RI utilization"
                            ],
                            metadata={
                                "instance_type": instance_type,
                                "region": region,
                                "instance_count": len(stable_instances),
                                "resource_ids": [r.resource_id for r in stable_instances]
                            }
                        )
                        opportunities.append(opportunity)
                        
            except Exception as e:
                logger.error(f"Failed to analyze RI opportunities for {instance_type}: {e}")
                continue
        
        return opportunities
    
    async def _analyze_spot_instance_opportunities(
        self, 
        resources: List[CloudResource]
    ) -> List[OptimizationOpportunity]:
        """Analyze Spot Instance opportunities for fault-tolerant workloads"""
        opportunities = []
        
        compute_resources = [r for r in resources if r.resource_type == "compute"]
        
        for resource in compute_resources:
            try:
                # Check if workload is suitable for spot instances
                is_suitable = await self._is_suitable_for_spot(resource)
                
                if is_suitable:
                    cost_data = await self._get_resource_cost_data(resource)
                    monthly_cost = cost_data.get('monthly_cost', 0)
                    
                    # Typical spot savings: 50-90%
                    spot_savings_percentage = 70.0
                    potential_savings = monthly_cost * (spot_savings_percentage / 100)
                    
                    if potential_savings > 50:  # Only recommend if savings > $50/month
                        opportunity = OptimizationOpportunity(
                            resource_id=resource.resource_id,
                            resource_name=resource.name or resource.resource_id,
                            optimization_type=OptimizationType.SPOT_INSTANCES,
                            priority=Priority.MEDIUM,
                            current_cost=monthly_cost,
                            potential_savings=potential_savings,
                            savings_percentage=spot_savings_percentage,
                            confidence_score=0.7,
                            implementation_effort="High",
                            risk_level="Medium",
                            description="Convert to Spot Instances for fault-tolerant workload",
                            action_steps=[
                                "Ensure application handles interruptions gracefully",
                                "Set up spot fleet or auto scaling with mixed instances",
                                "Implement checkpointing/state management",
                                "Monitor spot availability and pricing"
                            ],
                            metadata={
                                "instance_type": resource.instance_type,
                                "suitability_score": is_suitable.get('score', 0.7),
                                "workload_type": is_suitable.get('workload_type', 'unknown')
                            }
                        )
                        opportunities.append(opportunity)
                        
            except Exception as e:
                logger.error(f"Failed to analyze spot opportunities for {resource.resource_id}: {e}")
                continue
        
        return opportunities
    
    async def _analyze_storage_optimization(
        self, 
        resources: List[CloudResource]
    ) -> List[OptimizationOpportunity]:
        """Analyze storage optimization opportunities"""
        opportunities = []
        
        storage_resources = [r for r in resources if r.resource_type == "storage"]
        
        for resource in storage_resources:
            try:
                storage_metrics = await self._get_storage_metrics(resource)
                cost_data = await self._get_resource_cost_data(resource)
                
                if not storage_metrics:
                    continue
                
                monthly_cost = cost_data.get('monthly_cost', 0)
                
                # Check for storage tier optimization
                current_tier = storage_metrics.get('storage_class', 'standard')
                access_frequency = storage_metrics.get('access_frequency', 'unknown')
                
                if current_tier == 'standard' and access_frequency == 'infrequent':
                    # Recommend moving to infrequent access tier
                    savings_percentage = 40.0  # Typical IA savings
                    potential_savings = monthly_cost * (savings_percentage / 100)
                    
                    opportunity = OptimizationOpportunity(
                        resource_id=resource.resource_id,
                        resource_name=resource.name or resource.resource_id,
                        optimization_type=OptimizationType.STORAGE_OPTIMIZATION,
                        priority=Priority.MEDIUM,
                        current_cost=monthly_cost,
                        potential_savings=potential_savings,
                        savings_percentage=savings_percentage,
                        confidence_score=0.8,
                        implementation_effort="Low",
                        risk_level="Low",
                        description="Move to Infrequent Access storage tier",
                        action_steps=[
                            "Set up lifecycle policy",
                            "Move infrequently accessed data",
                            "Monitor access patterns",
                            "Adjust lifecycle rules as needed"
                        ],
                        metadata={
                            "current_tier": current_tier,
                            "recommended_tier": "infrequent_access",
                            "access_frequency": access_frequency
                        }
                    )
                    opportunities.append(opportunity)
                
                # Check for unused storage
                if storage_metrics.get('utilization', 100) < 20:
                    opportunity = OptimizationOpportunity(
                        resource_id=resource.resource_id,
                        resource_name=resource.name or resource.resource_id,
                        optimization_type=OptimizationType.STORAGE_OPTIMIZATION,
                        priority=Priority.HIGH,
                        current_cost=monthly_cost,
                        potential_savings=monthly_cost * 0.8,
                        savings_percentage=80.0,
                        confidence_score=0.9,
                        implementation_effort="Low",
                        risk_level="Low",
                        description="Storage volume appears to be mostly unused",
                        action_steps=[
                            "Verify data is not needed",
                            "Create backup if necessary",
                            "Delete or resize storage volume"
                        ],
                        metadata={
                            "utilization": storage_metrics.get('utilization', 0),
                            "size_gb": storage_metrics.get('size_gb', 0)
                        }
                    )
                    opportunities.append(opportunity)
                    
            except Exception as e:
                logger.error(f"Failed to analyze storage optimization for {resource.resource_id}: {e}")
                continue
        
        return opportunities
    
    async def _analyze_scheduled_scaling_opportunities(
        self, 
        resources: List[CloudResource]
    ) -> List[OptimizationOpportunity]:
        """Analyze opportunities for scheduled scaling based on usage patterns"""
        opportunities = []
        
        # Group resources by application/tag
        app_groups = {}
        for resource in resources:
            if resource.resource_type == "compute":
                app_name = resource.tags.get('Application', 'unknown')
                if app_name not in app_groups:
                    app_groups[app_name] = []
                app_groups[app_name].append(resource)
        
        for app_name, group_resources in app_groups.items():
            try:
                # Analyze usage patterns
                usage_patterns = await self._analyze_usage_patterns(group_resources)
                
                if usage_patterns.get('has_predictable_pattern'):
                    total_cost = sum([
                        (await self._get_resource_cost_data(r)).get('monthly_cost', 0)
                        for r in group_resources
                    ])
                    
                    # Estimate savings from scheduled scaling
                    off_hours_percentage = usage_patterns.get('off_hours_percentage', 50)
                    potential_savings = total_cost * (off_hours_percentage / 100) * 0.7  # 70% of off-hour costs
                    
                    if potential_savings > 200:  # Only recommend if savings > $200/month
                        opportunity = OptimizationOpportunity(
                            resource_id=f"scaling-{app_name}",
                            resource_name=f"Scheduled scaling for {app_name}",
                            optimization_type=OptimizationType.SCHEDULED_SCALING,
                            priority=Priority.MEDIUM,
                            current_cost=total_cost,
                            potential_savings=potential_savings,
                            savings_percentage=(potential_savings / total_cost) * 100,
                            confidence_score=usage_patterns.get('confidence', 0.7),
                            implementation_effort="High",
                            risk_level="Medium",
                            description=f"Implement scheduled scaling for {app_name} based on usage patterns",
                            action_steps=[
                                "Set up auto scaling groups",
                                "Configure scaling schedules",
                                "Implement application health checks",
                                "Monitor scaling events and adjust"
                            ],
                            metadata={
                                "application": app_name,
                                "resource_count": len(group_resources),
                                "usage_pattern": usage_patterns,
                                "off_hours_percentage": off_hours_percentage
                            }
                        )
                        opportunities.append(opportunity)
                        
            except Exception as e:
                logger.error(f"Failed to analyze scheduled scaling for {app_name}: {e}")
                continue
        
        return opportunities
    
    # Helper methods for data retrieval and analysis
    async def _get_resource_utilization(self, resource: CloudResource) -> Dict[str, Any]:
        """Get resource utilization metrics"""
        # This would integrate with cloud provider monitoring APIs
        # For now, return mock data
        return {
            'avg_cpu_utilization': 15.5,
            'max_cpu_utilization': 45.2,
            'avg_memory_utilization': 22.1,
            'max_memory_utilization': 38.9,
            'network_utilization': 5.3
        }
    
    async def _get_resource_cost_data(self, resource: CloudResource) -> Dict[str, Any]:
        """Get resource cost data"""
        # Query cost records for this resource
        cost_records = self.db.query(CostRecord).filter(
            CostRecord.resource_id == resource.id,
            CostRecord.date >= datetime.now() - timedelta(days=30)
        ).all()
        
        total_cost = sum([record.cost for record in cost_records])
        
        return {
            'monthly_cost': float(total_cost),
            'daily_average': float(total_cost / 30),
            'cost_trend': 'stable'  # Could calculate actual trend
        }
    
    async def _check_resource_idle(self, resource: CloudResource) -> Tuple[bool, Dict[str, Any]]:
        """Check if a resource is idle"""
        # This would check various metrics depending on resource type
        # For now, return mock analysis
        idle_days = 7  # Mock: resource has been idle for 7 days
        
        return True, {
            'confidence': 0.9,
            'idle_days': idle_days,
            'last_activity': datetime.now() - timedelta(days=idle_days),
            'activity_type': 'cpu_usage'
        }
    
    async def _get_resource_uptime_days(self, resource: CloudResource) -> int:
        """Get number of days the resource has been running"""
        if resource.launch_time:
            uptime = datetime.now() - resource.launch_time
            return uptime.days
        return 0
    
    async def _is_suitable_for_spot(self, resource: CloudResource) -> Dict[str, Any]:
        """Check if workload is suitable for spot instances"""
        # Analyze workload characteristics
        tags = resource.tags or {}
        workload_type = tags.get('WorkloadType', 'unknown')
        
        # Simple heuristic based on tags and patterns
        suitable_types = ['batch', 'development', 'testing', 'analytics']
        is_suitable = workload_type.lower() in suitable_types
        
        return {
            'suitable': is_suitable,
            'score': 0.8 if is_suitable else 0.3,
            'workload_type': workload_type
        }
    
    async def _get_storage_metrics(self, resource: CloudResource) -> Dict[str, Any]:
        """Get storage metrics"""
        # Mock storage metrics
        return {
            'storage_class': 'standard',
            'access_frequency': 'infrequent',
            'utilization': 15.5,  # Percentage used
            'size_gb': 1000,
            'iops_utilization': 25.2
        }
    
    async def _analyze_usage_patterns(self, resources: List[CloudResource]) -> Dict[str, Any]:
        """Analyze usage patterns for a group of resources"""
        # Mock pattern analysis
        return {
            'has_predictable_pattern': True,
            'confidence': 0.8,
            'off_hours_percentage': 60,  # 60% of time is off-hours
            'peak_hours': '09:00-17:00',
            'weekend_usage': 20  # 20% usage on weekends
        }
    
    async def _generate_downsize_recommendation(
        self, 
        resource: CloudResource, 
        utilization: Dict[str, Any], 
        cost_data: Dict[str, Any]
    ) -> Optional[OptimizationOpportunity]:
        """Generate a downsize recommendation"""
        current_cost = cost_data.get('monthly_cost', 0)
        
        # Estimate savings from downsizing (typically 30-50%)
        savings_percentage = 40.0
        potential_savings = current_cost * (savings_percentage / 100)
        
        return OptimizationOpportunity(
            resource_id=resource.resource_id,
            resource_name=resource.name or resource.resource_id,
            optimization_type=OptimizationType.RIGHTSIZING,
            priority=Priority.HIGH if potential_savings > 500 else Priority.MEDIUM,
            current_cost=current_cost,
            potential_savings=potential_savings,
            savings_percentage=savings_percentage,
            confidence_score=0.85,
            implementation_effort="Medium",
            risk_level="Low",
            description=f"Downsize from {resource.instance_type} due to low utilization",
            action_steps=[
                "Monitor performance impact during off-peak hours",
                "Create instance snapshot/backup",
                "Resize to smaller instance type",
                "Monitor performance for 48 hours"
            ],
            metadata={
                "current_instance_type": resource.instance_type,
                "avg_cpu_utilization": utilization.get('avg_cpu_utilization', 0),
                "max_cpu_utilization": utilization.get('max_cpu_utilization', 0),
                "recommended_action": "downsize"
            }
        )
    
    async def _generate_upsize_recommendation(
        self, 
        resource: CloudResource, 
        utilization: Dict[str, Any], 
        cost_data: Dict[str, Any]
    ) -> Optional[OptimizationOpportunity]:
        """Generate an upsize recommendation"""
        # This is more about performance than cost savings
        # Could calculate cost of performance impact vs. upsize cost
        return None  # Typically not a cost optimization