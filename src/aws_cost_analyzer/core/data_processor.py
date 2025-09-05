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
                    
                    parsed_data.append({
                        'Date': time_period,
                        'Service': service,
                        'Region': region,
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
