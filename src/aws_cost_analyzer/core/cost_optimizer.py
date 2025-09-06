"""
成本优化建议引擎
"""
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from ..utils.logger import get_logger

logger = get_logger()


class CostOptimizationAnalyzer:
    """成本优化分析器"""
    
    def __init__(self):
        """初始化成本优化分析器"""
        # 定义各服务的优化阈值
        self.service_thresholds = {
            'Amazon Elastic Compute Cloud - Compute': {
                'idle_threshold': 5.0,  # 低于此费用被认为是闲置
                'optimization_potential': 0.6  # 优化潜力
            },
            'Amazon Relational Database Service': {
                'idle_threshold': 10.0,
                'optimization_potential': 0.4
            },
            'Amazon Simple Storage Service': {
                'idle_threshold': 1.0,
                'optimization_potential': 0.3
            },
            'Amazon Elastic Load Balancing': {
                'idle_threshold': 20.0,
                'optimization_potential': 0.8
            }
        }
    
    def analyze_cost_optimization_opportunities(
        self,
        df: pd.DataFrame,
        service_costs: pd.DataFrame,
        resource_costs: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        分析成本优化机会
        
        Args:
            df: 费用数据
            service_costs: 服务费用数据
            resource_costs: 资源费用数据
            
        Returns:
            优化建议字典
        """
        if df.empty:
            return {}
        
        optimization_report = {
            'total_potential_savings': 0.0,
            'optimization_opportunities': [],
            'service_recommendations': {},
            'resource_recommendations': [],
            'general_recommendations': [],
            'priority_actions': []
        }
        
        # 1. 分析服务级优化机会
        service_opportunities = self._analyze_service_optimization(service_costs)
        optimization_report['service_recommendations'] = service_opportunities
        
        # 2. 分析资源级优化机会
        resource_opportunities = []
        if resource_costs is not None and not resource_costs.empty:
            resource_opportunities = self._analyze_resource_optimization(resource_costs)
            optimization_report['resource_recommendations'] = resource_opportunities
        
        # 3. 分析费用趋势和异常
        trend_analysis = self._analyze_cost_trends(df)
        optimization_report['trend_insights'] = trend_analysis
        
        # 4. 生成通用建议
        general_recommendations = self._generate_general_recommendations(df, service_costs)
        optimization_report['general_recommendations'] = general_recommendations
        
        # 5. 计算总体潜在节省
        total_savings = self._calculate_total_potential_savings(
            service_opportunities, 
            resource_opportunities
        )
        optimization_report['total_potential_savings'] = total_savings
        
        # 6. 生成优先级行动计划
        priority_actions = self._generate_priority_actions(optimization_report)
        optimization_report['priority_actions'] = priority_actions
        
        return optimization_report
    
    def _analyze_service_optimization(self, service_costs: pd.DataFrame) -> Dict[str, Any]:
        """分析服务级优化机会"""
        if service_costs.empty:
            return {}
        
        recommendations = {}
        
        for service_idx, row in service_costs.iterrows():
            service_name = service_idx if isinstance(service_idx, str) else str(service_idx)
            total_cost = row['总费用']
            record_count = row['记录数']
            avg_cost = row['平均费用']
            
            service_rec = {
                'current_cost': total_cost,
                'optimization_potential': 0.0,
                'potential_savings': 0.0,
                'recommendations': [],
                'confidence': 'medium'
            }
            
            # EC2优化建议
            if 'Elastic Compute Cloud' in service_name or 'EC2' in service_name:
                ec2_recommendations = self._analyze_ec2_optimization(total_cost, avg_cost, record_count)
                service_rec['recommendations'].extend(ec2_recommendations['recommendations'])
                service_rec['potential_savings'] += ec2_recommendations['potential_savings']
                service_rec['optimization_potential'] = ec2_recommendations['optimization_potential']
            
            # RDS优化建议
            elif 'Relational Database' in service_name or 'RDS' in service_name:
                rds_recommendations = self._analyze_rds_optimization(total_cost, avg_cost, record_count)
                service_rec['recommendations'].extend(rds_recommendations['recommendations'])
                service_rec['potential_savings'] += rds_recommendations['potential_savings']
            
            # S3优化建议
            elif 'Simple Storage Service' in service_name or 'S3' in service_name:
                s3_recommendations = self._analyze_s3_optimization(total_cost, avg_cost, record_count)
                service_rec['recommendations'].extend(s3_recommendations['recommendations'])
                service_rec['potential_savings'] += s3_recommendations['potential_savings']
            
            # ELB优化建议
            elif 'Load Balancing' in service_name or 'ELB' in service_name:
                elb_recommendations = self._analyze_elb_optimization(total_cost, avg_cost, record_count)
                service_rec['recommendations'].extend(elb_recommendations['recommendations'])
                service_rec['potential_savings'] += elb_recommendations['potential_savings']
            
            # 通用优化建议
            else:
                generic_recommendations = self._analyze_generic_service_optimization(
                    service_name, total_cost, avg_cost, record_count
                )
                service_rec['recommendations'].extend(generic_recommendations['recommendations'])
                service_rec['potential_savings'] += generic_recommendations['potential_savings']
            
            if service_rec['recommendations']:
                recommendations[service_name] = service_rec
        
        return recommendations
    
    def _analyze_ec2_optimization(self, total_cost: float, avg_cost: float, record_count: int) -> Dict[str, Any]:
        """分析EC2优化建议"""
        recommendations = []
        potential_savings = 0.0
        optimization_potential = 0.0
        
        # 低利用率实例检测
        if avg_cost < 50.0 and record_count > 10:
            recommendations.append({
                'type': 'right_sizing',
                'priority': 'high',
                'description': '检测到可能的低利用率EC2实例，建议进行右调优化',
                'action': '考虑降级实例类型或使用Spot实例',
                'potential_savings': total_cost * 0.3
            })
            potential_savings += total_cost * 0.3
            optimization_potential = 0.3
        
        # 预留实例建议
        if total_cost > 500.0:
            recommendations.append({
                'type': 'reserved_instances',
                'priority': 'medium',
                'description': f'EC2费用较高(${total_cost:.2f})，建议考虑预留实例',
                'action': '购买1年期预留实例可节省20-30%成本',
                'potential_savings': total_cost * 0.25
            })
            potential_savings += total_cost * 0.25
            optimization_potential = max(optimization_potential, 0.25)
        
        # Spot实例建议
        if record_count > 5:
            recommendations.append({
                'type': 'spot_instances',
                'priority': 'medium', 
                'description': '考虑在合适的工作负载中使用Spot实例',
                'action': '对于容错性强的任务，使用Spot实例可节省50-70%',
                'potential_savings': total_cost * 0.15
            })
            potential_savings += total_cost * 0.15
        
        return {
            'recommendations': recommendations,
            'potential_savings': potential_savings,
            'optimization_potential': optimization_potential
        }
    
    def _analyze_rds_optimization(self, total_cost: float, avg_cost: float, record_count: int) -> Dict[str, Any]:
        """分析RDS优化建议"""
        recommendations = []
        potential_savings = 0.0
        
        if avg_cost < 100.0 and record_count > 5:
            recommendations.append({
                'type': 'rds_right_sizing',
                'priority': 'medium',
                'description': '检测到可能过度配置的RDS实例',
                'action': '监控CPU和内存使用率，考虑降级实例类型',
                'potential_savings': total_cost * 0.2
            })
            potential_savings += total_cost * 0.2
        
        if total_cost > 200.0:
            recommendations.append({
                'type': 'rds_reserved',
                'priority': 'high',
                'description': 'RDS费用较高，强烈建议使用预留实例',
                'action': '购买预留实例可节省30-50%的RDS成本',
                'potential_savings': total_cost * 0.4
            })
            potential_savings += total_cost * 0.4
        
        return {
            'recommendations': recommendations,
            'potential_savings': potential_savings
        }
    
    def _analyze_s3_optimization(self, total_cost: float, avg_cost: float, record_count: int) -> Dict[str, Any]:
        """分析S3优化建议"""
        recommendations = []
        potential_savings = 0.0
        
        recommendations.append({
            'type': 's3_storage_class',
            'priority': 'low',
            'description': '优化S3存储类别以降低成本',
            'action': '将不常访问数据迁移到IA或Glacier存储类别',
            'potential_savings': total_cost * 0.3
        })
        potential_savings += total_cost * 0.3
        
        if total_cost > 100.0:
            recommendations.append({
                'type': 's3_lifecycle',
                'priority': 'medium',
                'description': '设置S3生命周期策略自动管理数据',
                'action': '配置自动转换和删除策略，可节省20-40%存储成本',
                'potential_savings': total_cost * 0.25
            })
            potential_savings += total_cost * 0.25
        
        return {
            'recommendations': recommendations,
            'potential_savings': potential_savings
        }
    
    def _analyze_elb_optimization(self, total_cost: float, avg_cost: float, record_count: int) -> Dict[str, Any]:
        """分析ELB优化建议"""
        recommendations = []
        potential_savings = 0.0
        
        if avg_cost < 20.0:
            recommendations.append({
                'type': 'elb_consolidation',
                'priority': 'medium',
                'description': '检测到低流量负载均衡器，考虑合并',
                'action': '合并低流量的负载均衡器以减少固定成本',
                'potential_savings': total_cost * 0.4
            })
            potential_savings += total_cost * 0.4
        
        return {
            'recommendations': recommendations,
            'potential_savings': potential_savings
        }
    
    def _analyze_generic_service_optimization(
        self, 
        service_name: str, 
        total_cost: float, 
        avg_cost: float, 
        record_count: int
    ) -> Dict[str, Any]:
        """分析通用服务优化建议"""
        recommendations = []
        potential_savings = 0.0
        
        # 基于费用的通用建议
        if total_cost > 100.0:
            recommendations.append({
                'type': 'cost_monitoring',
                'priority': 'low',
                'description': f'{service_name}费用较高，建议加强监控',
                'action': '设置费用告警和使用量监控',
                'potential_savings': total_cost * 0.1
            })
            potential_savings += total_cost * 0.1
        
        return {
            'recommendations': recommendations,
            'potential_savings': potential_savings
        }
    
    def _analyze_resource_optimization(self, resource_costs: pd.DataFrame) -> List[Dict[str, Any]]:
        """分析资源级优化机会"""
        if resource_costs.empty:
            return []
        
        recommendations = []
        
        # 识别高成本资源
        high_cost_resources = resource_costs[resource_costs['总费用'] > resource_costs['总费用'].quantile(0.8)]
        
        for _, resource in high_cost_resources.iterrows():
            recommendations.append({
                'resource_id': resource['ResourceId'],
                'service': resource['Service'],
                'current_cost': resource['总费用'],
                'recommendation': f'高成本资源，建议深入分析使用情况',
                'potential_action': '监控资源使用率，考虑优化或替换',
                'priority': 'high' if resource['总费用'] > 1000 else 'medium'
            })
        
        # 识别可能闲置的资源
        low_cost_resources = resource_costs[resource_costs['总费用'] < resource_costs['总费用'].quantile(0.2)]
        
        for _, resource in low_cost_resources.head(5).iterrows():  # 只取前5个
            recommendations.append({
                'resource_id': resource['ResourceId'],
                'service': resource['Service'],
                'current_cost': resource['总费用'],
                'recommendation': '低成本资源，可能未充分利用',
                'potential_action': '检查资源是否仍需要，考虑删除或调整配置',
                'priority': 'low'
            })
        
        return recommendations
    
    def _analyze_cost_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析费用趋势洞察"""
        if df.empty:
            return {}
        
        # 按日期聚合费用
        daily_costs = df.groupby('Date')['Cost'].sum().reset_index()
        daily_costs['Date'] = pd.to_datetime(daily_costs['Date'])
        daily_costs = daily_costs.sort_values('Date')
        
        if len(daily_costs) < 2:
            return {'trend': 'insufficient_data'}
        
        # 计算变化率
        recent_avg = daily_costs.tail(7)['Cost'].mean()  # 最近7天平均
        earlier_avg = daily_costs.head(7)['Cost'].mean()  # 前7天平均
        
        if earlier_avg > 0:
            change_rate = (recent_avg - earlier_avg) / earlier_avg * 100
        else:
            change_rate = 0
        
        insights = {
            'trend_direction': 'increasing' if change_rate > 5 else 'decreasing' if change_rate < -5 else 'stable',
            'change_rate': round(change_rate, 2),
            'recent_avg_cost': round(recent_avg, 2),
            'recommendations': []
        }
        
        if change_rate > 20:
            insights['recommendations'].append({
                'type': 'cost_spike_investigation',
                'priority': 'high',
                'description': f'费用增长率达到{change_rate:.1f}%，需要紧急调查',
                'action': '立即检查新增资源和使用量异常'
            })
        elif change_rate > 10:
            insights['recommendations'].append({
                'type': 'cost_trend_monitoring',
                'priority': 'medium',
                'description': f'费用呈上升趋势({change_rate:.1f}%)，建议加强监控',
                'action': '分析费用增长原因并设置告警'
            })
        
        return insights
    
    def _generate_general_recommendations(self, df: pd.DataFrame, service_costs: pd.DataFrame) -> List[Dict[str, Any]]:
        """生成通用优化建议"""
        recommendations = []
        
        total_cost = df['Cost'].sum()
        
        # 基于总费用的建议
        if total_cost > 1000:
            recommendations.append({
                'category': 'cost_governance',
                'priority': 'high',
                'title': '建立成本治理机制',
                'description': f'总费用达到${total_cost:.2f}，建议建立完整的成本管理体系',
                'actions': [
                    '设置预算告警和成本阈值',
                    '建立定期成本审核机制', 
                    '使用AWS Cost Categories和标签进行成本分类',
                    '考虑使用AWS Organizations进行统一管理'
                ]
            })
        
        # 服务多样性建议
        service_count = len(service_costs)
        if service_count > 10:
            recommendations.append({
                'category': 'service_consolidation',
                'priority': 'medium',
                'title': '服务整合优化',
                'description': f'使用了{service_count}个AWS服务，考虑整合优化',
                'actions': [
                    '评估每个服务的必要性',
                    '考虑使用多功能服务替代单一功能服务',
                    '优化服务间的数据传输成本'
                ]
            })
        
        # 监控和可视化建议
        recommendations.append({
            'category': 'monitoring_optimization',
            'priority': 'medium',
            'title': '增强监控和可视化',
            'description': '建立全面的成本监控体系',
            'actions': [
                '使用AWS Cost Explorer进行深入分析',
                '设置CloudWatch费用监控仪表板',
                '建立自动化费用报告系统',
                '定期进行成本优化审核'
            ]
        })
        
        return recommendations
    
    def _calculate_total_potential_savings(
        self, 
        service_opportunities: Dict[str, Any], 
        resource_opportunities: List[Dict[str, Any]]
    ) -> float:
        """计算总体潜在节省"""
        total_savings = 0.0
        
        # 服务级节省
        for service, rec in service_opportunities.items():
            total_savings += rec.get('potential_savings', 0.0)
        
        # 资源级节省（估算）
        for resource in resource_opportunities:
            if resource.get('priority') == 'high':
                # 高优先级资源假设可节省20%
                total_savings += resource.get('current_cost', 0.0) * 0.2
            elif resource.get('priority') == 'medium':
                # 中优先级资源假设可节省10%
                total_savings += resource.get('current_cost', 0.0) * 0.1
        
        return round(total_savings, 2)
    
    def _generate_priority_actions(self, optimization_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优先级行动计划"""
        actions = []
        
        # 收集所有高优先级建议
        high_priority_savings = 0.0
        
        # 从服务建议中提取高优先级行动
        for service, rec in optimization_report.get('service_recommendations', {}).items():
            for recommendation in rec.get('recommendations', []):
                if recommendation.get('priority') == 'high':
                    actions.append({
                        'priority': 1,
                        'category': 'service_optimization',
                        'service': service,
                        'action': recommendation.get('action'),
                        'potential_savings': recommendation.get('potential_savings', 0),
                        'description': recommendation.get('description')
                    })
                    high_priority_savings += recommendation.get('potential_savings', 0)
        
        # 从资源建议中提取高优先级行动
        for resource in optimization_report.get('resource_recommendations', []):
            if resource.get('priority') == 'high':
                actions.append({
                    'priority': 1,
                    'category': 'resource_optimization',
                    'resource': resource.get('resource_id'),
                    'action': resource.get('potential_action'),
                    'potential_savings': resource.get('current_cost', 0) * 0.2,
                    'description': resource.get('recommendation')
                })
        
        # 从趋势分析中提取紧急行动
        trend_insights = optimization_report.get('trend_insights', {})
        for rec in trend_insights.get('recommendations', []):
            if rec.get('priority') == 'high':
                actions.append({
                    'priority': 0,  # 最高优先级
                    'category': 'urgent_investigation',
                    'action': rec.get('action'),
                    'description': rec.get('description')
                })
        
        # 按优先级排序
        actions.sort(key=lambda x: x['priority'])
        
        return actions[:10]  # 返回前10个优先级最高的行动
    
    def generate_optimization_report_html(self, optimization_report: Dict[str, Any]) -> str:
        """生成优化建议的HTML报告片段"""
        if not optimization_report:
            return '<div class="no-data">暂无优化建议</div>'
        
        total_savings = optimization_report.get('total_potential_savings', 0)
        priority_actions = optimization_report.get('priority_actions', [])
        
        html = f'''
        <div class="optimization-report">
            <div class="optimization-summary">
                <div class="savings-highlight">
                    <h3>💰 潜在节省总额</h3>
                    <div class="savings-amount">${total_savings:.2f}</div>
                    <p>通过实施以下优化建议，您可能节省的费用</p>
                </div>
            </div>
            
            <div class="priority-actions">
                <h3>🎯 优先行动计划</h3>
                <div class="action-list">
        '''
        
        for i, action in enumerate(priority_actions[:5], 1):
            priority_badge = '🔥' if action['priority'] == 0 else '⚡' if action['priority'] == 1 else '📋'
            savings = action.get('potential_savings', 0)
            
            html += f'''
                <div class="action-item priority-{action['priority']}">
                    <div class="action-header">
                        <span class="priority-badge">{priority_badge}</span>
                        <span class="action-title">行动 {i}</span>
                        {f'<span class="savings-badge">${savings:.2f}</span>' if savings > 0 else ''}
                    </div>
                    <div class="action-description">{action.get('description', '')}</div>
                    <div class="action-detail">{action.get('action', '')}</div>
                </div>
            '''
        
        html += '''
                </div>
            </div>
        </div>
        
        <style>
        .optimization-report {
            margin: 2rem 0;
        }
        
        .optimization-summary {
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .savings-highlight h3 {
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }
        
        .savings-amount {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .priority-actions h3 {
            color: #2c3e50;
            margin-bottom: 1.5rem;
            font-size: 1.4rem;
        }
        
        .action-item {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-left: 4px solid #3498db;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .action-item.priority-0 {
            border-left-color: #e74c3c;
            background: #fdf2f2;
        }
        
        .action-item.priority-1 {
            border-left-color: #f39c12;
            background: #fefbf3;
        }
        
        .action-header {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 0.5rem;
        }
        
        .priority-badge {
            font-size: 1.2rem;
        }
        
        .action-title {
            font-weight: 600;
            color: #2c3e50;
            flex-grow: 1;
        }
        
        .savings-badge {
            background: #2ecc71;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        .action-description {
            color: #34495e;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .action-detail {
            color: #7f8c8d;
            font-size: 0.9rem;
            line-height: 1.4;
        }
        </style>
        '''
        
        return html