"""
Real-time Cost Monitoring and Alerting System
"""
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import aioredis
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.config import get_settings
from ..models.cloud_account import CostRecord
from ..models.business_intelligence import Anomaly
from ..utils.notifications import NotificationService
from ..utils.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)
settings = get_settings()

class AlertSeverity(str, Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AlertType(str, Enum):
    """Types of alerts"""
    COST_SPIKE = "cost_spike"
    BUDGET_EXCEEDED = "budget_exceeded"
    UNUSUAL_USAGE = "unusual_usage"
    IDLE_RESOURCES = "idle_resources"
    EFFICIENCY_DROP = "efficiency_drop"
    ANOMALY_DETECTED = "anomaly_detected"
    FORECAST_BREACH = "forecast_breach"

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    timestamp: datetime
    organization_id: str
    entity_type: str
    entity_id: str
    current_value: float
    threshold_value: float
    change_percentage: float
    metadata: Dict[str, Any]
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None

@dataclass
class MonitoringMetric:
    """Real-time monitoring metric"""
    metric_name: str
    value: float
    timestamp: datetime
    organization_id: str
    entity_type: str
    entity_id: str
    dimensions: Dict[str, str]

class RealTimeMonitor:
    """Real-time cost monitoring and alerting system"""
    
    def __init__(self):
        self.redis = None
        self.websocket_manager = WebSocketManager()
        self.notification_service = NotificationService()
        self.active_alerts: Dict[str, Alert] = {}
        self.monitoring_rules: Dict[str, Dict] = {}
        self.is_running = False
        
    async def initialize(self):
        """Initialize the monitoring system"""
        try:
            # Initialize Redis connection
            self.redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Load monitoring rules
            await self._load_monitoring_rules()
            
            logger.info("Real-time monitoring system initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring system: {e}")
            raise
    
    async def start_monitoring(self):
        """Start the real-time monitoring process"""
        if self.is_running:
            logger.warning("Monitoring system is already running")
            return
            
        self.is_running = True
        logger.info("Starting real-time monitoring system")
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._monitor_cost_streams()),
            asyncio.create_task(self._monitor_usage_patterns()),
            asyncio.create_task(self._detect_anomalies()),
            asyncio.create_task(self._process_alert_queue()),
            asyncio.create_task(self._cleanup_old_alerts())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Monitoring system error: {e}")
            self.is_running = False
            raise
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        self.is_running = False
        logger.info("Stopping real-time monitoring system")
        
        if self.redis:
            await self.redis.close()
    
    async def ingest_metric(self, metric: MonitoringMetric):
        """Ingest a real-time metric"""
        try:
            # Store metric in Redis time series
            metric_key = f"metrics:{metric.organization_id}:{metric.entity_type}:{metric.entity_id}:{metric.metric_name}"
            
            # Store in Redis with TTL
            await self.redis.zadd(
                metric_key,
                {json.dumps(asdict(metric)): metric.timestamp.timestamp()}
            )
            
            # Keep only last 24 hours of data
            cutoff_time = (datetime.now() - timedelta(hours=24)).timestamp()
            await self.redis.zremrangebyscore(metric_key, 0, cutoff_time)
            
            # Check for alerts
            await self._check_metric_alerts(metric)
            
            # Broadcast to WebSocket clients
            await self.websocket_manager.broadcast_metric(metric)
            
        except Exception as e:
            logger.error(f"Failed to ingest metric: {e}")
    
    async def _load_monitoring_rules(self):
        """Load monitoring rules from database"""
        # This would load from database, for now using hardcoded rules
        self.monitoring_rules = {
            "cost_spike": {
                "threshold_percentage": 50.0,  # 50% increase
                "time_window_minutes": 60,
                "severity": AlertSeverity.HIGH
            },
            "budget_exceeded": {
                "threshold_percentage": 100.0,  # 100% of budget
                "severity": AlertSeverity.CRITICAL
            },
            "unusual_usage": {
                "threshold_percentage": 200.0,  # 200% of normal
                "time_window_minutes": 30,
                "severity": AlertSeverity.MEDIUM
            },
            "efficiency_drop": {
                "threshold_percentage": -20.0,  # 20% decrease in efficiency
                "time_window_minutes": 120,
                "severity": AlertSeverity.MEDIUM
            }
        }
        
        logger.info(f"Loaded {len(self.monitoring_rules)} monitoring rules")
    
    async def _monitor_cost_streams(self):
        """Monitor real-time cost streams"""
        while self.is_running:
            try:
                # Get recent cost data from Redis streams
                cost_streams = await self._get_cost_streams()
                
                for stream_data in cost_streams:
                    await self._process_cost_stream(stream_data)
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring cost streams: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_usage_patterns(self):
        """Monitor usage patterns for anomalies"""
        while self.is_running:
            try:
                # Analyze usage patterns
                organizations = await self._get_active_organizations()
                
                for org_id in organizations:
                    await self._analyze_usage_patterns(org_id)
                
                # Wait before next analysis
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error monitoring usage patterns: {e}")
                await asyncio.sleep(300)
    
    async def _detect_anomalies(self):
        """Detect cost and usage anomalies"""
        while self.is_running:
            try:
                # Run anomaly detection
                organizations = await self._get_active_organizations()
                
                for org_id in organizations:
                    anomalies = await self._run_anomaly_detection(org_id)
                    
                    for anomaly in anomalies:
                        await self._create_anomaly_alert(anomaly)
                
                # Wait before next detection
                await asyncio.sleep(600)  # Check every 10 minutes
                
            except Exception as e:
                logger.error(f"Error detecting anomalies: {e}")
                await asyncio.sleep(600)
    
    async def _process_alert_queue(self):
        """Process pending alerts"""
        while self.is_running:
            try:
                # Process alert queue from Redis
                alert_data = await self.redis.blpop("alert_queue", timeout=10)
                
                if alert_data:
                    alert_json = alert_data[1]
                    alert_dict = json.loads(alert_json)
                    alert = Alert(**alert_dict)
                    
                    await self._process_alert(alert)
                
            except Exception as e:
                logger.error(f"Error processing alert queue: {e}")
                await asyncio.sleep(5)
    
    async def _cleanup_old_alerts(self):
        """Clean up old resolved alerts"""
        while self.is_running:
            try:
                # Remove alerts older than 7 days
                cutoff_time = datetime.now() - timedelta(days=7)
                
                alerts_to_remove = []
                for alert_id, alert in self.active_alerts.items():
                    if alert.is_resolved and alert.resolved_at and alert.resolved_at < cutoff_time:
                        alerts_to_remove.append(alert_id)
                
                for alert_id in alerts_to_remove:
                    del self.active_alerts[alert_id]
                
                logger.info(f"Cleaned up {len(alerts_to_remove)} old alerts")
                
                # Wait before next cleanup
                await asyncio.sleep(3600)  # Cleanup every hour
                
            except Exception as e:
                logger.error(f"Error cleaning up alerts: {e}")
                await asyncio.sleep(3600)
    
    async def _check_metric_alerts(self, metric: MonitoringMetric):
        """Check if metric triggers any alerts"""
        try:
            # Check cost spike alerts
            if metric.metric_name == "hourly_cost":
                await self._check_cost_spike_alert(metric)
            
            # Check usage alerts
            elif metric.metric_name in ["cpu_utilization", "memory_utilization"]:
                await self._check_usage_alert(metric)
            
            # Check efficiency alerts
            elif metric.metric_name == "cost_efficiency":
                await self._check_efficiency_alert(metric)
            
        except Exception as e:
            logger.error(f"Error checking metric alerts: {e}")
    
    async def _check_cost_spike_alert(self, metric: MonitoringMetric):
        """Check for cost spike alerts"""
        try:
            # Get historical data for comparison
            historical_data = await self._get_historical_metric_data(
                metric.organization_id,
                metric.entity_type,
                metric.entity_id,
                metric.metric_name,
                hours=24
            )
            
            if len(historical_data) < 10:  # Need enough data for comparison
                return
            
            # Calculate baseline (average of last 24 hours, excluding last hour)
            baseline_values = [d['value'] for d in historical_data[:-1]]
            baseline_avg = sum(baseline_values) / len(baseline_values)
            
            # Check for spike
            spike_threshold = self.monitoring_rules["cost_spike"]["threshold_percentage"]
            if baseline_avg > 0:
                change_percentage = ((metric.value - baseline_avg) / baseline_avg) * 100
                
                if change_percentage >= spike_threshold:
                    alert = Alert(
                        id=f"cost_spike_{metric.organization_id}_{metric.entity_id}_{int(metric.timestamp.timestamp())}",
                        alert_type=AlertType.COST_SPIKE,
                        severity=AlertSeverity.HIGH,
                        title="Cost Spike Detected",
                        description=f"Cost increased by {change_percentage:.1f}% in the last hour",
                        timestamp=metric.timestamp,
                        organization_id=metric.organization_id,
                        entity_type=metric.entity_type,
                        entity_id=metric.entity_id,
                        current_value=metric.value,
                        threshold_value=baseline_avg * (1 + spike_threshold / 100),
                        change_percentage=change_percentage,
                        metadata={
                            "baseline_cost": baseline_avg,
                            "spike_threshold": spike_threshold,
                            "metric_name": metric.metric_name
                        }
                    )
                    
                    await self._trigger_alert(alert)
            
        except Exception as e:
            logger.error(f"Error checking cost spike alert: {e}")
    
    async def _check_usage_alert(self, metric: MonitoringMetric):
        """Check for unusual usage alerts"""
        try:
            # Get recent usage pattern
            recent_data = await self._get_historical_metric_data(
                metric.organization_id,
                metric.entity_type,
                metric.entity_id,
                metric.metric_name,
                hours=1
            )
            
            # Simple threshold-based alert (could be made more sophisticated)
            if metric.metric_name == "cpu_utilization" and metric.value > 90:
                alert = Alert(
                    id=f"high_cpu_{metric.organization_id}_{metric.entity_id}_{int(metric.timestamp.timestamp())}",
                    alert_type=AlertType.UNUSUAL_USAGE,
                    severity=AlertSeverity.MEDIUM,
                    title="High CPU Utilization",
                    description=f"CPU utilization is at {metric.value:.1f}%",
                    timestamp=metric.timestamp,
                    organization_id=metric.organization_id,
                    entity_type=metric.entity_type,
                    entity_id=metric.entity_id,
                    current_value=metric.value,
                    threshold_value=90.0,
                    change_percentage=0.0,
                    metadata={
                        "metric_name": metric.metric_name,
                        "threshold": 90.0
                    }
                )
                
                await self._trigger_alert(alert)
            
        except Exception as e:
            logger.error(f"Error checking usage alert: {e}")
    
    async def _check_efficiency_alert(self, metric: MonitoringMetric):
        """Check for efficiency drop alerts"""
        try:
            # Get historical efficiency data
            historical_data = await self._get_historical_metric_data(
                metric.organization_id,
                metric.entity_type,
                metric.entity_id,
                metric.metric_name,
                hours=24
            )
            
            if len(historical_data) < 10:
                return
            
            # Calculate baseline efficiency
            baseline_values = [d['value'] for d in historical_data[:-2]]
            baseline_avg = sum(baseline_values) / len(baseline_values)
            
            # Check for efficiency drop
            drop_threshold = self.monitoring_rules["efficiency_drop"]["threshold_percentage"]
            if baseline_avg > 0:
                change_percentage = ((metric.value - baseline_avg) / baseline_avg) * 100
                
                if change_percentage <= drop_threshold:  # Negative threshold
                    alert = Alert(
                        id=f"efficiency_drop_{metric.organization_id}_{metric.entity_id}_{int(metric.timestamp.timestamp())}",
                        alert_type=AlertType.EFFICIENCY_DROP,
                        severity=AlertSeverity.MEDIUM,
                        title="Cost Efficiency Drop",
                        description=f"Cost efficiency decreased by {abs(change_percentage):.1f}%",
                        timestamp=metric.timestamp,
                        organization_id=metric.organization_id,
                        entity_type=metric.entity_type,
                        entity_id=metric.entity_id,
                        current_value=metric.value,
                        threshold_value=baseline_avg * (1 + drop_threshold / 100),
                        change_percentage=change_percentage,
                        metadata={
                            "baseline_efficiency": baseline_avg,
                            "drop_threshold": drop_threshold,
                            "metric_name": metric.metric_name
                        }
                    )
                    
                    await self._trigger_alert(alert)
            
        except Exception as e:
            logger.error(f"Error checking efficiency alert: {e}")
    
    async def _trigger_alert(self, alert: Alert):
        """Trigger an alert"""
        try:
            # Check if similar alert already exists
            similar_alert_id = await self._find_similar_alert(alert)
            if similar_alert_id:
                logger.debug(f"Similar alert {similar_alert_id} already exists, skipping")
                return
            
            # Add to active alerts
            self.active_alerts[alert.id] = alert
            
            # Send notifications
            await self.notification_service.send_alert_notification(alert)
            
            # Broadcast to WebSocket clients
            await self.websocket_manager.broadcast_alert(alert)
            
            # Store in database for persistence
            await self._store_alert_in_db(alert)
            
            logger.info(f"Alert triggered: {alert.title} ({alert.severity})")
            
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    async def _find_similar_alert(self, alert: Alert) -> Optional[str]:
        """Find if a similar alert already exists"""
        for existing_id, existing_alert in self.active_alerts.items():
            if (existing_alert.alert_type == alert.alert_type and
                existing_alert.organization_id == alert.organization_id and
                existing_alert.entity_id == alert.entity_id and
                not existing_alert.is_resolved and
                (alert.timestamp - existing_alert.timestamp).total_seconds() < 3600):  # Within 1 hour
                return existing_id
        return None
    
    async def _get_historical_metric_data(
        self, 
        organization_id: str, 
        entity_type: str, 
        entity_id: str, 
        metric_name: str, 
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get historical metric data from Redis"""
        try:
            metric_key = f"metrics:{organization_id}:{entity_type}:{entity_id}:{metric_name}"
            
            # Get data from last N hours
            start_time = (datetime.now() - timedelta(hours=hours)).timestamp()
            end_time = datetime.now().timestamp()
            
            raw_data = await self.redis.zrangebyscore(
                metric_key, start_time, end_time, withscores=True
            )
            
            data = []
            for item, timestamp in raw_data:
                metric_data = json.loads(item)
                data.append({
                    'value': metric_data['value'],
                    'timestamp': datetime.fromtimestamp(timestamp)
                })
            
            return sorted(data, key=lambda x: x['timestamp'])
            
        except Exception as e:
            logger.error(f"Error getting historical metric data: {e}")
            return []
    
    async def _get_active_organizations(self) -> List[str]:
        """Get list of active organization IDs"""
        # This would query the database for active organizations
        # For now, return mock data
        return ["org-1", "org-2", "org-3"]
    
    async def _get_cost_streams(self) -> List[Dict[str, Any]]:
        """Get recent cost stream data"""
        # This would integrate with cloud provider cost APIs
        # For now, return mock data
        return []
    
    async def _process_cost_stream(self, stream_data: Dict[str, Any]):
        """Process a cost stream"""
        # Process individual cost stream entry
        pass
    
    async def _analyze_usage_patterns(self, organization_id: str):
        """Analyze usage patterns for an organization"""
        # Perform usage pattern analysis
        pass
    
    async def _run_anomaly_detection(self, organization_id: str) -> List[Dict[str, Any]]:
        """Run anomaly detection for an organization"""
        # Run ML-based anomaly detection
        return []
    
    async def _create_anomaly_alert(self, anomaly: Dict[str, Any]):
        """Create alert from detected anomaly"""
        # Convert anomaly to alert
        pass
    
    async def _process_alert(self, alert: Alert):
        """Process a single alert"""
        # Process alert (send notifications, store, etc.)
        await self._trigger_alert(alert)
    
    async def _store_alert_in_db(self, alert: Alert):
        """Store alert in database for persistence"""
        try:
            # This would store the alert in the database
            # For now, just log it
            logger.info(f"Storing alert in database: {alert.id}")
            
        except Exception as e:
            logger.error(f"Error storing alert in database: {e}")
    
    # Public API methods
    async def get_active_alerts(self, organization_id: str) -> List[Alert]:
        """Get active alerts for an organization"""
        return [
            alert for alert in self.active_alerts.values()
            if alert.organization_id == organization_id and not alert.is_resolved
        ]
    
    async def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """Resolve an alert"""
        try:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.is_resolved = True
                alert.resolved_at = datetime.now()
                alert.metadata['resolved_by'] = resolved_by
                
                # Broadcast resolution
                await self.websocket_manager.broadcast_alert_resolution(alert)
                
                logger.info(f"Alert {alert_id} resolved by {resolved_by}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error resolving alert {alert_id}: {e}")
            return False
    
    async def get_metrics_summary(self, organization_id: str) -> Dict[str, Any]:
        """Get real-time metrics summary"""
        try:
            # Get recent metrics for organization
            metric_keys = await self.redis.keys(f"metrics:{organization_id}:*")
            
            summary = {
                "total_metrics": len(metric_keys),
                "active_alerts": len(await self.get_active_alerts(organization_id)),
                "last_updated": datetime.now().isoformat(),
                "metrics_by_type": {},
                "recent_activity": []
            }
            
            # Count metrics by type
            for key in metric_keys:
                parts = key.split(":")
                if len(parts) >= 4:
                    entity_type = parts[2]
                    summary["metrics_by_type"][entity_type] = summary["metrics_by_type"].get(entity_type, 0) + 1
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {}

# Global monitoring instance
monitoring_system = RealTimeMonitor()