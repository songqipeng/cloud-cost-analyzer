"""
Advanced Cost Allocation and Chargeback System
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..core.database import get_db
from ..models.cloud_account import CostRecord, CloudResource
from ..models.organization import Team, Project
from ..models.business_intelligence import CostAllocation, BusinessEntity
from ..utils.formatters import format_currency

logger = logging.getLogger(__name__)

class AllocationMethod(str, Enum):
    """Cost allocation methods"""
    DIRECT = "direct"                    # Direct assignment via tags
    PROPORTIONAL = "proportional"       # Proportional by usage/resources
    EQUAL_SPLIT = "equal_split"         # Equal split among entities
    WEIGHTED = "weighted"               # Weighted allocation
    TIME_BASED = "time_based"           # Based on time usage
    ACTIVITY_BASED = "activity_based"   # Based on activity metrics
    CUSTOM_RULES = "custom_rules"       # Custom allocation rules

class AllocationDimension(str, Enum):
    """Allocation dimensions"""
    TEAM = "team"
    PROJECT = "project"
    COST_CENTER = "cost_center"
    DEPARTMENT = "department"
    ENVIRONMENT = "environment"
    APPLICATION = "application"
    CUSTOMER = "customer"
    FEATURE = "feature"

@dataclass
class AllocationRule:
    """Cost allocation rule"""
    id: str
    name: str
    description: str
    method: AllocationMethod
    dimension: AllocationDimension
    priority: int
    conditions: List[Dict[str, Any]]
    weights: Dict[str, float]
    is_active: bool
    metadata: Dict[str, Any]

@dataclass
class AllocationResult:
    """Result of cost allocation"""
    cost_record_id: str
    original_cost: Decimal
    allocated_cost: Decimal
    allocation_method: AllocationMethod
    allocation_dimension: AllocationDimension
    allocated_to_id: str
    allocated_to_name: str
    allocation_weight: float
    confidence_score: float
    metadata: Dict[str, Any]

class CostAllocationEngine:
    """Advanced cost allocation engine"""
    
    def __init__(self, db: Session):
        self.db = db
        self.allocation_rules: List[AllocationRule] = []
        self.load_allocation_rules()
    
    def load_allocation_rules(self):
        """Load allocation rules from database/configuration"""
        # For now, using hardcoded rules. In production, these would come from database
        self.allocation_rules = [
            AllocationRule(
                id="direct_tag_allocation",
                name="Direct Tag Allocation",
                description="Allocate costs based on direct resource tags",
                method=AllocationMethod.DIRECT,
                dimension=AllocationDimension.TEAM,
                priority=1,
                conditions=[{"tag_exists": ["Team", "team", "owner"]}],
                weights={},
                is_active=True,
                metadata={"tag_keys": ["Team", "team", "owner"]}
            ),
            AllocationRule(
                id="project_proportional",
                name="Project Proportional Allocation",
                description="Allocate shared costs proportionally by project usage",
                method=AllocationMethod.PROPORTIONAL,
                dimension=AllocationDimension.PROJECT,
                priority=2,
                conditions=[{"service_type": ["compute", "storage"]}],
                weights={},
                is_active=True,
                metadata={"allocation_basis": "resource_count"}
            ),
            AllocationRule(
                id="shared_services_equal",
                name="Shared Services Equal Split",
                description="Split shared service costs equally among teams",
                method=AllocationMethod.EQUAL_SPLIT,
                dimension=AllocationDimension.TEAM,
                priority=3,
                conditions=[{"service_name": ["CloudWatch", "CloudTrail", "IAM"]}],
                weights={},
                is_active=True,
                metadata={"shared_services": True}
            ),
            AllocationRule(
                id="environment_weighted",
                name="Environment Weighted Allocation",
                description="Allocate environment costs by weighted usage",
                method=AllocationMethod.WEIGHTED,
                dimension=AllocationDimension.ENVIRONMENT,
                priority=4,
                conditions=[{"tag_exists": ["Environment", "env"]}],
                weights={"production": 0.6, "staging": 0.3, "development": 0.1},
                is_active=True,
                metadata={"weight_basis": "resource_hours"}
            )
        ]
        
        logger.info(f"Loaded {len(self.allocation_rules)} allocation rules")
    
    async def allocate_costs(
        self, 
        organization_id: str,
        start_date: datetime,
        end_date: datetime,
        force_reallocate: bool = False
    ) -> Dict[str, Any]:
        """Allocate costs for a given time period"""
        logger.info(f"Starting cost allocation for organization {organization_id} from {start_date} to {end_date}")
        
        # Get cost records for the period
        cost_records = self._get_cost_records(organization_id, start_date, end_date)
        
        if not cost_records:
            logger.info("No cost records found for allocation")
            return {"total_records": 0, "allocated_records": 0, "total_cost": 0}
        
        allocation_results = []
        total_allocated_cost = Decimal('0')
        successful_allocations = 0
        
        # Process cost records in batches
        batch_size = 1000
        for i in range(0, len(cost_records), batch_size):
            batch = cost_records[i:i + batch_size]
            batch_results = await self._allocate_cost_batch(batch, force_reallocate)
            
            allocation_results.extend(batch_results)
            successful_allocations += len(batch_results)
            total_allocated_cost += sum(result.allocated_cost for result in batch_results)
        
        # Store allocation results
        await self._store_allocation_results(allocation_results)
        
        logger.info(f"Allocated {successful_allocations}/{len(cost_records)} cost records, total: {total_allocated_cost}")
        
        return {
            "total_records": len(cost_records),
            "allocated_records": successful_allocations,
            "total_cost": float(total_allocated_cost),
            "allocation_rate": (successful_allocations / len(cost_records)) * 100 if cost_records else 0
        }
    
    async def _allocate_cost_batch(
        self, 
        cost_records: List[CostRecord],
        force_reallocate: bool
    ) -> List[AllocationResult]:
        """Allocate a batch of cost records"""
        results = []
        
        for cost_record in cost_records:
            try:
                # Skip if already allocated (unless force reallocate)
                if not force_reallocate and await self._is_already_allocated(cost_record.id):
                    continue
                
                # Find applicable allocation rule
                allocation_rule = self._find_applicable_rule(cost_record)
                
                if not allocation_rule:
                    logger.debug(f"No allocation rule found for cost record {cost_record.id}")
                    continue
                
                # Perform allocation based on rule
                allocation_results = await self._apply_allocation_rule(cost_record, allocation_rule)
                results.extend(allocation_results)
                
            except Exception as e:
                logger.error(f"Failed to allocate cost record {cost_record.id}: {e}")
                continue
        
        return results
    
    def _find_applicable_rule(self, cost_record: CostRecord) -> Optional[AllocationRule]:
        """Find the most applicable allocation rule for a cost record"""
        applicable_rules = []
        
        for rule in self.allocation_rules:
            if not rule.is_active:
                continue
                
            if self._rule_matches_cost_record(rule, cost_record):
                applicable_rules.append(rule)
        
        # Return rule with highest priority (lowest priority number)
        if applicable_rules:
            return sorted(applicable_rules, key=lambda r: r.priority)[0]
        
        return None
    
    def _rule_matches_cost_record(self, rule: AllocationRule, cost_record: CostRecord) -> bool:
        """Check if an allocation rule matches a cost record"""
        for condition in rule.conditions:
            if "tag_exists" in condition:
                # Check if resource has required tags
                if cost_record.resource:
                    resource_tags = cost_record.resource.tags or {}
                    tag_keys = condition["tag_exists"]
                    if not any(key in resource_tags for key in tag_keys):
                        return False
                else:
                    return False
            
            if "service_type" in condition:
                # Check service type
                if cost_record.resource:
                    if cost_record.resource.resource_type not in condition["service_type"]:
                        return False
                else:
                    return False
            
            if "service_name" in condition:
                # Check service name
                if cost_record.service_name not in condition["service_name"]:
                    return False
        
        return True
    
    async def _apply_allocation_rule(
        self, 
        cost_record: CostRecord, 
        rule: AllocationRule
    ) -> List[AllocationResult]:
        """Apply an allocation rule to a cost record"""
        if rule.method == AllocationMethod.DIRECT:
            return await self._apply_direct_allocation(cost_record, rule)
        elif rule.method == AllocationMethod.PROPORTIONAL:
            return await self._apply_proportional_allocation(cost_record, rule)
        elif rule.method == AllocationMethod.EQUAL_SPLIT:
            return await self._apply_equal_split_allocation(cost_record, rule)
        elif rule.method == AllocationMethod.WEIGHTED:
            return await self._apply_weighted_allocation(cost_record, rule)
        else:
            logger.warning(f"Unsupported allocation method: {rule.method}")
            return []
    
    async def _apply_direct_allocation(
        self, 
        cost_record: CostRecord, 
        rule: AllocationRule
    ) -> List[AllocationResult]:
        """Apply direct allocation based on tags"""
        results = []
        
        if not cost_record.resource:
            return results
        
        resource_tags = cost_record.resource.tags or {}
        tag_keys = rule.metadata.get("tag_keys", [])
        
        # Find the tag value for allocation
        allocation_target = None
        for tag_key in tag_keys:
            if tag_key in resource_tags:
                allocation_target = resource_tags[tag_key]
                break
        
        if not allocation_target:
            return results
        
        # Find the entity to allocate to
        entity = await self._find_allocation_entity(rule.dimension, allocation_target)
        
        if entity:
            result = AllocationResult(
                cost_record_id=cost_record.id,
                original_cost=Decimal(str(cost_record.cost)),
                allocated_cost=Decimal(str(cost_record.cost)),
                allocation_method=rule.method,
                allocation_dimension=rule.dimension,
                allocated_to_id=entity["id"],
                allocated_to_name=entity["name"],
                allocation_weight=1.0,
                confidence_score=0.95,
                metadata={
                    "rule_id": rule.id,
                    "tag_key": next(k for k in tag_keys if k in resource_tags),
                    "tag_value": allocation_target
                }
            )
            results.append(result)
        
        return results
    
    async def _apply_proportional_allocation(
        self, 
        cost_record: CostRecord, 
        rule: AllocationRule
    ) -> List[AllocationResult]:
        """Apply proportional allocation"""
        results = []
        
        # Get entities for proportional allocation
        entities = await self._get_entities_for_allocation(rule.dimension)
        
        if not entities:
            return results
        
        # Calculate proportional weights based on usage
        weights = await self._calculate_proportional_weights(entities, rule)
        
        if not weights:
            return results
        
        # Allocate cost proportionally
        total_cost = Decimal(str(cost_record.cost))
        
        for entity_id, weight in weights.items():
            entity = next((e for e in entities if e["id"] == entity_id), None)
            if entity:
                allocated_amount = total_cost * Decimal(str(weight))
                
                result = AllocationResult(
                    cost_record_id=cost_record.id,
                    original_cost=total_cost,
                    allocated_cost=allocated_amount,
                    allocation_method=rule.method,
                    allocation_dimension=rule.dimension,
                    allocated_to_id=entity["id"],
                    allocated_to_name=entity["name"],
                    allocation_weight=weight,
                    confidence_score=0.8,
                    metadata={
                        "rule_id": rule.id,
                        "allocation_basis": rule.metadata.get("allocation_basis", "resource_count")
                    }
                )
                results.append(result)
        
        return results
    
    async def _apply_equal_split_allocation(
        self, 
        cost_record: CostRecord, 
        rule: AllocationRule
    ) -> List[AllocationResult]:
        """Apply equal split allocation"""
        results = []
        
        # Get entities for equal split
        entities = await self._get_entities_for_allocation(rule.dimension)
        
        if not entities:
            return results
        
        # Split cost equally
        total_cost = Decimal(str(cost_record.cost))
        split_amount = total_cost / len(entities)
        equal_weight = 1.0 / len(entities)
        
        for entity in entities:
            result = AllocationResult(
                cost_record_id=cost_record.id,
                original_cost=total_cost,
                allocated_cost=split_amount,
                allocation_method=rule.method,
                allocation_dimension=rule.dimension,
                allocated_to_id=entity["id"],
                allocated_to_name=entity["name"],
                allocation_weight=equal_weight,
                confidence_score=0.7,
                metadata={
                    "rule_id": rule.id,
                    "split_count": len(entities)
                }
            )
            results.append(result)
        
        return results
    
    async def _apply_weighted_allocation(
        self, 
        cost_record: CostRecord, 
        rule: AllocationRule
    ) -> List[AllocationResult]:
        """Apply weighted allocation"""
        results = []
        
        # Get predefined weights from rule
        weights = rule.weights
        
        if not weights:
            return results
        
        # Normalize weights to sum to 1.0
        total_weight = sum(weights.values())
        normalized_weights = {k: v / total_weight for k, v in weights.items()}
        
        # Allocate cost by weights
        total_cost = Decimal(str(cost_record.cost))
        
        for entity_key, weight in normalized_weights.items():
            # Find entity by key (could be environment name, team name, etc.)
            entity = await self._find_allocation_entity(rule.dimension, entity_key)
            
            if entity:
                allocated_amount = total_cost * Decimal(str(weight))
                
                result = AllocationResult(
                    cost_record_id=cost_record.id,
                    original_cost=total_cost,
                    allocated_cost=allocated_amount,
                    allocation_method=rule.method,
                    allocation_dimension=rule.dimension,
                    allocated_to_id=entity["id"],
                    allocated_to_name=entity["name"],
                    allocation_weight=weight,
                    confidence_score=0.85,
                    metadata={
                        "rule_id": rule.id,
                        "weight_key": entity_key
                    }
                )
                results.append(result)
        
        return results
    
    async def _find_allocation_entity(
        self, 
        dimension: AllocationDimension, 
        identifier: str
    ) -> Optional[Dict[str, str]]:
        """Find an entity for allocation"""
        if dimension == AllocationDimension.TEAM:
            team = self.db.query(Team).filter(
                or_(Team.name == identifier, Team.id == identifier)
            ).first()
            if team:
                return {"id": team.id, "name": team.name}
        
        elif dimension == AllocationDimension.PROJECT:
            project = self.db.query(Project).filter(
                or_(Project.name == identifier, Project.id == identifier)
            ).first()
            if project:
                return {"id": project.id, "name": project.name}
        
        # Add other dimension lookups as needed
        
        return None
    
    async def _get_entities_for_allocation(self, dimension: AllocationDimension) -> List[Dict[str, str]]:
        """Get all entities for a given allocation dimension"""
        entities = []
        
        if dimension == AllocationDimension.TEAM:
            teams = self.db.query(Team).filter(Team.is_deleted == False).all()
            entities = [{"id": t.id, "name": t.name} for t in teams]
        
        elif dimension == AllocationDimension.PROJECT:
            projects = self.db.query(Project).filter(Project.is_deleted == False).all()
            entities = [{"id": p.id, "name": p.name} for p in projects]
        
        # Add other dimensions as needed
        
        return entities
    
    async def _calculate_proportional_weights(
        self, 
        entities: List[Dict[str, str]], 
        rule: AllocationRule
    ) -> Dict[str, float]:
        """Calculate proportional weights for entities"""
        weights = {}
        allocation_basis = rule.metadata.get("allocation_basis", "resource_count")
        
        if allocation_basis == "resource_count":
            # Allocate based on number of resources per entity
            for entity in entities:
                if rule.dimension == AllocationDimension.TEAM:
                    resource_count = self.db.query(CloudResource).filter(
                        CloudResource.team_id == entity["id"],
                        CloudResource.is_deleted == False
                    ).count()
                elif rule.dimension == AllocationDimension.PROJECT:
                    resource_count = self.db.query(CloudResource).filter(
                        CloudResource.project_id == entity["id"],
                        CloudResource.is_deleted == False
                    ).count()
                else:
                    resource_count = 1
                
                weights[entity["id"]] = resource_count
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        return weights
    
    def _get_cost_records(
        self, 
        organization_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[CostRecord]:
        """Get cost records for allocation"""
        return self.db.query(CostRecord).join(CostRecord.account).filter(
            CostRecord.account.has(organization_id=organization_id),
            CostRecord.date >= start_date,
            CostRecord.date <= end_date
        ).all()
    
    async def _is_already_allocated(self, cost_record_id: str) -> bool:
        """Check if cost record is already allocated"""
        existing = self.db.query(CostAllocation).filter(
            CostAllocation.cost_record_id == cost_record_id
        ).first()
        return existing is not None
    
    async def _store_allocation_results(self, results: List[AllocationResult]):
        """Store allocation results in database"""
        try:
            allocations = []
            for result in results:
                allocation = CostAllocation(
                    date=datetime.now(),
                    billing_period=datetime.now().strftime("%Y-%m"),
                    allocated_cost=result.allocated_cost,
                    allocation_method=result.allocation_method.value,
                    allocation_weight=result.allocation_weight,
                    business_entity_id=result.allocated_to_id,
                    cost_record_id=result.cost_record_id,
                    allocation_rules=result.metadata,
                    confidence_score=result.confidence_score
                )
                allocations.append(allocation)
            
            self.db.add_all(allocations)
            self.db.commit()
            
            logger.info(f"Stored {len(allocations)} allocation results")
            
        except Exception as e:
            logger.error(f"Failed to store allocation results: {e}")
            self.db.rollback()
            raise

class ChargebackReportGenerator:
    """Generate chargeback and showback reports"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_team_chargeback_report(
        self, 
        organization_id: str,
        start_date: datetime,
        end_date: datetime,
        include_unallocated: bool = True
    ) -> Dict[str, Any]:
        """Generate team chargeback report"""
        
        # Get team allocations
        team_allocations = self.db.query(
            CostAllocation.business_entity_id.label('team_id'),
            func.sum(CostAllocation.allocated_cost).label('total_cost'),
            func.count(CostAllocation.id).label('allocation_count')
        ).join(CostAllocation.business_entity).filter(
            CostAllocation.date >= start_date,
            CostAllocation.date <= end_date
        ).group_by(CostAllocation.business_entity_id).all()
        
        # Get team details
        teams = self.db.query(Team).filter(
            Team.organization_id == organization_id
        ).all()
        team_dict = {team.id: team for team in teams}
        
        # Build report
        report_data = []
        total_allocated = Decimal('0')
        
        for allocation in team_allocations:
            team = team_dict.get(allocation.team_id)
            if team:
                cost = Decimal(str(allocation.total_cost))
                total_allocated += cost
                
                report_data.append({
                    "team_id": team.id,
                    "team_name": team.name,
                    "cost_center": team.cost_center,
                    "allocated_cost": float(cost),
                    "allocation_count": allocation.allocation_count,
                    "budget": team.budget_monthly,
                    "budget_utilization": (float(cost) / float(team.budget_monthly)) * 100 if team.budget_monthly else None
                })
        
        # Calculate unallocated costs if requested
        unallocated_cost = Decimal('0')
        if include_unallocated:
            total_org_cost = self._get_total_organization_cost(organization_id, start_date, end_date)
            unallocated_cost = total_org_cost - total_allocated
        
        return {
            "report_type": "team_chargeback",
            "organization_id": organization_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_allocated_cost": float(total_allocated),
                "unallocated_cost": float(unallocated_cost),
                "allocation_rate": (float(total_allocated) / float(total_allocated + unallocated_cost)) * 100 if (total_allocated + unallocated_cost) > 0 else 0,
                "team_count": len(report_data)
            },
            "teams": sorted(report_data, key=lambda x: x["allocated_cost"], reverse=True)
        }
    
    async def generate_project_chargeback_report(
        self, 
        organization_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate project chargeback report"""
        
        # Similar to team report but for projects
        project_allocations = self.db.query(
            CostAllocation.business_entity_id.label('project_id'),
            func.sum(CostAllocation.allocated_cost).label('total_cost'),
            func.count(CostAllocation.id).label('allocation_count')
        ).join(CostAllocation.business_entity).filter(
            CostAllocation.date >= start_date,
            CostAllocation.date <= end_date
        ).group_by(CostAllocation.business_entity_id).all()
        
        # Get project details
        projects = self.db.query(Project).join(Project.team).filter(
            Project.team.has(organization_id=organization_id)
        ).all()
        project_dict = {project.id: project for project in projects}
        
        # Build report
        report_data = []
        total_allocated = Decimal('0')
        
        for allocation in project_allocations:
            project = project_dict.get(allocation.project_id)
            if project:
                cost = Decimal(str(allocation.total_cost))
                total_allocated += cost
                
                report_data.append({
                    "project_id": project.id,
                    "project_name": project.name,
                    "team_name": project.team.name,
                    "cost_center": project.cost_center,
                    "allocated_cost": float(cost),
                    "allocation_count": allocation.allocation_count,
                    "budget": project.budget_monthly,
                    "budget_utilization": (float(cost) / float(project.budget_monthly)) * 100 if project.budget_monthly else None
                })
        
        return {
            "report_type": "project_chargeback",
            "organization_id": organization_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {
                "total_allocated_cost": float(total_allocated),
                "project_count": len(report_data)
            },
            "projects": sorted(report_data, key=lambda x: x["allocated_cost"], reverse=True)
        }
    
    def _get_total_organization_cost(
        self, 
        organization_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Decimal:
        """Get total cost for organization in period"""
        result = self.db.query(
            func.sum(CostRecord.cost)
        ).join(CostRecord.account).filter(
            CostRecord.account.has(organization_id=organization_id),
            CostRecord.date >= start_date,
            CostRecord.date <= end_date
        ).scalar()
        
        return Decimal(str(result)) if result else Decimal('0')