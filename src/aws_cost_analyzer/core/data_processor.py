"""
数据处理模块
"""
import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class DataProcessor:
    """数据处理类"""
    
    def __init__(self, cost_threshold: float = 0.01):
        """
        初始化数据处理器
        
        Args:
            cost_threshold: 最小费用阈值
        """
        self.cost_threshold = cost_threshold
    
    def parse_cost_data(self, cost_data: Dict[str, Any]) -> pd.DataFrame:
        """
        解析AWS费用数据
        
        Args:
            cost_data: AWS费用数据
            
        Returns:
            解析后的费用数据DataFrame
        """
        if not cost_data:
            return pd.DataFrame()
        
        parsed_data = []
        
        try:
            for result in cost_data.get('ResultsByTime', []):
                time_period = result['TimePeriod']['Start']
                
                for group in result.get('Groups', []):
                    keys = group['Keys']
                    cost = group['Metrics']['UnblendedCost']['Amount']
                    unit = group['Metrics']['UnblendedCost']['Unit']
                    
                    # 解析分组键
                    service = keys[0] if len(keys) > 0 else 'Unknown'
                    region = keys[1] if len(keys) > 1 else 'Unknown'
                    resource_id = keys[2] if len(keys) > 2 else 'Unknown'
                    
                    parsed_data.append({
                        'Date': time_period,
                        'Service': service,
                        'Region': region,
                        'ResourceId': resource_id,
                        'Cost': float(cost),
                        'Unit': unit
                    })
        except Exception as e:
            raise Exception(f"数据解析失败: {e}")
        
        if not parsed_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(parsed_data)
        df['Date'] = pd.to_datetime(df['Date'])
        
        return df
    
    def filter_cost_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        过滤费用数据
        
        Args:
            df: 原始费用数据
            
        Returns:
            过滤后的费用数据
        """
        if df.empty:
            return df
        
        # 过滤掉费用低于阈值的记录
        filtered_df = df[df['Cost'] >= self.cost_threshold].copy()
        
        # 过滤掉无区域信息
        filtered_df = filtered_df[filtered_df['Region'] != 'NoRegion'].copy()
        
        return filtered_df
    
    def analyze_costs_by_service(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        按服务分析费用
        
        Args:
            df: 费用数据
            
        Returns:
            按服务分组的费用统计
        """
        if df.empty:
            return pd.DataFrame()
        
        # 过滤数据
        filtered_df = self.filter_cost_data(df)
        
        if filtered_df.empty:
            return pd.DataFrame()
        
        # 按服务分组统计
        service_stats = filtered_df.groupby('Service').agg({
            'Cost': ['sum', 'mean', 'count']
        }).round(4)
        
        # 重命名列
        service_stats.columns = ['总费用', '平均费用', '记录数']
        service_stats = service_stats.sort_values('总费用', ascending=False)
        
        return service_stats
    
    def analyze_costs_by_region(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        按区域分析费用
        
        Args:
            df: 费用数据
            
        Returns:
            按区域分组的费用统计
        """
        if df.empty:
            return pd.DataFrame()
        
        # 过滤数据
        filtered_df = self.filter_cost_data(df)
        
        if filtered_df.empty:
            return pd.DataFrame()
        
        # 按区域分组统计
        region_stats = filtered_df.groupby('Region').agg({
            'Cost': ['sum', 'mean', 'count']
        }).round(4)
        
        # 重命名列
        region_stats.columns = ['总费用', '平均费用', '记录数']
        region_stats = region_stats.sort_values('总费用', ascending=False)
        
        return region_stats
    
    def analyze_costs_by_resource(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        按资源分析费用
        
        Args:
            df: 费用数据
            
        Returns:
            按资源分组的费用统计
        """
        if df.empty or 'ResourceId' not in df.columns:
            return pd.DataFrame()
        
        # 过滤掉Unknown资源
        resource_df = df[df['ResourceId'] != 'Unknown'].copy()
        
        if resource_df.empty:
            return pd.DataFrame()
        
        # 按资源ID分组统计
        resource_summary = resource_df.groupby(['Service', 'ResourceId']).agg({
            'Cost': ['sum', 'mean', 'count'],
            'Region': 'first'
        }).round(4)
        
        # 重构列名
        resource_summary.columns = ['总费用', '平均费用', '记录数', '区域']
        resource_summary = resource_summary.reset_index()
        
        # 按总费用排序
        resource_summary = resource_summary.sort_values('总费用', ascending=False)
        
        return resource_summary
    
    def analyze_costs_by_time(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        按时间分析费用
        
        Args:
            df: 费用数据
            
        Returns:
            按时间分组的费用统计
        """
        if df.empty:
            return pd.DataFrame()
        
        # 按日期分组统计
        time_stats = df.groupby('Date').agg({
            'Cost': ['sum', 'mean', 'count']
        }).round(4)
        
        # 重命名列
        time_stats.columns = ['总费用', '平均费用', '记录数']
        time_stats = time_stats.sort_index()
        
        return time_stats
    
    def get_cost_summary(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        获取费用摘要
        
        Args:
            df: 费用数据
            
        Returns:
            费用摘要字典
        """
        if df.empty:
            return {
                'total_cost': 0.0,
                'avg_daily_cost': 0.0,
                'max_daily_cost': 0.0,
                'min_daily_cost': 0.0
            }
        
        # 按日期汇总费用
        daily_costs = df.groupby('Date')['Cost'].sum()
        
        return {
            'total_cost': df['Cost'].sum(),
            'avg_daily_cost': daily_costs.mean(),
            'max_daily_cost': daily_costs.max(),
            'min_daily_cost': daily_costs.min()
        }
    
    def detect_cost_anomalies(self, df: pd.DataFrame, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """
        检测费用异常
        
        Args:
            df: 费用数据
            threshold: 异常检测阈值（标准差倍数）
            
        Returns:
            异常记录列表
        """
        if df.empty:
            return []
        
        anomalies = []
        
        # 按日期汇总费用
        daily_costs = df.groupby('Date')['Cost'].sum()
        
        if len(daily_costs) < 3:
            return []
        
        # 计算统计指标
        mean_cost = daily_costs.mean()
        std_cost = daily_costs.std()
        
        # 检测异常
        for date, cost in daily_costs.items():
            if abs(cost - mean_cost) > threshold * std_cost:
                anomalies.append({
                    'date': date,
                    'cost': cost,
                    'deviation': (cost - mean_cost) / std_cost,
                    'type': 'high' if cost > mean_cost else 'low'
                })
        
        return anomalies
    
    def analyze_cost_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        分析费用趋势
        
        Args:
            df: 费用数据
            
        Returns:
            趋势分析结果
        """
        if df.empty:
            return {}
        
        # 确保日期列为datetime类型
        df_copy = df.copy()
        df_copy['Date'] = pd.to_datetime(df_copy['Date'])
        
        # 按日期聚合
        daily_costs = df_copy.groupby('Date')['Cost'].sum().reset_index()
        daily_costs = daily_costs.sort_values('Date')
        
        if len(daily_costs) < 2:
            return {'trend': 'insufficient_data'}
        
        # 计算变化率
        daily_costs['cost_change'] = daily_costs['Cost'].pct_change()
        daily_costs['cost_change_abs'] = daily_costs['Cost'].diff()
        
        # 计算趋势指标
        avg_cost = daily_costs['Cost'].mean()
        max_cost = daily_costs['Cost'].max()
        min_cost = daily_costs['Cost'].min()
        avg_change_rate = daily_costs['cost_change'].mean()
        
        # 识别趋势方向
        if avg_change_rate > 0.05:  # 5%以上增长
            trend_direction = 'increasing'
        elif avg_change_rate < -0.05:  # 5%以上下降
            trend_direction = 'decreasing'
        else:
            trend_direction = 'stable'
        
        return {
            'trend': trend_direction,
            'avg_cost': round(avg_cost, 2),
            'max_cost': round(max_cost, 2),
            'min_cost': round(min_cost, 2),
            'avg_change_rate': round(avg_change_rate * 100, 2),
            'volatility': round(daily_costs['Cost'].std(), 2),
            'total_days': len(daily_costs)
        }
    
    def calculate_cost_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        计算费用趋势
        
        Args:
            df: 费用数据
            
        Returns:
            趋势分析结果
        """
        if df.empty:
            return {'trend': 'stable', 'change_rate': 0.0, 'direction': 'none'}
        
        # 按日期汇总费用
        daily_costs = df.groupby('Date')['Cost'].sum().sort_index()
        
        if len(daily_costs) < 2:
            return {'trend': 'stable', 'change_rate': 0.0, 'direction': 'none'}
        
        # 计算趋势
        first_half = daily_costs[:len(daily_costs)//2].mean()
        second_half = daily_costs[len(daily_costs)//2:].mean()
        
        change_rate = (second_half - first_half) / first_half * 100
        
        if abs(change_rate) < 5:
            trend = 'stable'
        elif change_rate > 0:
            trend = 'increasing'
        else:
            trend = 'decreasing'
        
        return {
            'trend': trend,
            'change_rate': change_rate,
            'direction': 'up' if change_rate > 0 else 'down' if change_rate < 0 else 'stable'
        }
    
    def get_top_services(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        获取费用最高的服务
        
        Args:
            df: 费用数据
            top_n: 返回前N个服务
            
        Returns:
            费用最高的服务列表
        """
        service_stats = self.analyze_costs_by_service(df)
        return service_stats.head(top_n)
    
    def get_top_regions(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        获取费用最高的区域
        
        Args:
            df: 费用数据
            top_n: 返回前N个区域
            
        Returns:
            费用最高的区域列表
        """
        region_stats = self.analyze_costs_by_region(df)
        return region_stats.head(top_n)
    
    def get_top_resources(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        获取费用最高的资源
        
        Args:
            df: 费用数据
            top_n: 返回前N个资源
            
        Returns:
            费用最高的资源列表
        """
        resource_stats = self.analyze_costs_by_resource(df)
        return resource_stats.head(top_n)
    
    def get_resource_utilization_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        获取资源利用率洞察
        
        Args:
            df: 费用数据
            
        Returns:
            资源利用率分析结果
        """
        if df.empty or 'ResourceId' not in df.columns:
            return {}
        
        # 统计各类型资源数量
        resource_counts = df[df['ResourceId'] != 'Unknown'].groupby('Service')['ResourceId'].nunique()
        
        # 计算每个资源的平均费用
        resource_avg_costs = df[df['ResourceId'] != 'Unknown'].groupby(['Service', 'ResourceId'])['Cost'].mean()
        
        # 识别高成本资源
        high_cost_threshold = resource_avg_costs.quantile(0.8)
        high_cost_resources = resource_avg_costs[resource_avg_costs > high_cost_threshold]
        
        # 识别低成本资源（可能未充分利用）
        low_cost_threshold = resource_avg_costs.quantile(0.2)
        low_cost_resources = resource_avg_costs[resource_avg_costs < low_cost_threshold]
        
        return {
            'total_unique_resources': resource_counts.sum(),
            'resources_by_service': resource_counts.to_dict(),
            'high_cost_resource_count': len(high_cost_resources),
            'low_cost_resource_count': len(low_cost_resources),
            'avg_cost_per_resource': round(resource_avg_costs.mean(), 2),
            'cost_distribution': {
                'high_threshold': round(high_cost_threshold, 2),
                'low_threshold': round(low_cost_threshold, 2)
            }
        }
