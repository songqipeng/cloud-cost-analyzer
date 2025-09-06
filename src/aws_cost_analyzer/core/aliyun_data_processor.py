"""
阿里云数据处理模块
"""
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger()


class AliyunDataProcessor:
    """阿里云费用数据处理器"""
    
    def __init__(self, cost_threshold: float = 0.01):
        """
        初始化数据处理器
        
        Args:
            cost_threshold: 费用过滤阈值
        """
        self.cost_threshold = cost_threshold
    
    def parse_cost_data(self, cost_data: Dict[str, Any]) -> pd.DataFrame:
        """
        解析阿里云费用数据
        
        Args:
            cost_data: 阿里云费用数据
            
        Returns:
            解析后的DataFrame
        """
        if not cost_data:
            logger.warning("阿里云费用数据为空")
            return pd.DataFrame()
        
        try:
            all_records = []
            
            # 处理实例级别数据
            instance_data = cost_data.get('instance_data', [])
            for item in instance_data:
                record = {
                    'Date': item.get('billing_date', ''),
                    'Service': item.get('product_name', 'Unknown'),
                    'Region': item.get('region', 'Unknown'),
                    'Cost': float(item.get('pretax_amount', 0)),
                    'Currency': item.get('currency', 'CNY'),
                    'Provider': 'aliyun',
                    'ResourceId': item.get('instance_id', ''),
                    'ResourceName': item.get('instance_name', ''),
                    'SubscriptionType': item.get('subscription_type', ''),
                    'Zone': item.get('zone', '')
                }
                
                # 过滤低于阈值的费用
                if record['Cost'] >= self.cost_threshold:
                    all_records.append(record)
            
            # 处理产品级别数据（如果实例数据为空）
            if not all_records:
                product_data = cost_data.get('product_data', [])
                for item in product_data:
                    record = {
                        'Date': item.get('billing_date', ''),
                        'Service': item.get('product_name', 'Unknown'),
                        'Region': 'Unknown',  # 产品级别数据通常没有区域信息
                        'Cost': float(item.get('pretax_amount', 0)),
                        'Currency': item.get('currency', 'CNY'),
                        'Provider': 'aliyun',
                        'ResourceId': '',
                        'ResourceName': '',
                        'SubscriptionType': item.get('subscription_type', ''),
                        'ProductCode': item.get('product_code', '')
                    }
                    
                    # 过滤低于阈值的费用
                    if record['Cost'] >= self.cost_threshold:
                        all_records.append(record)
            
            if not all_records:
                logger.warning("没有找到符合条件的阿里云费用记录")
                return pd.DataFrame()
            
            # 创建DataFrame
            df = pd.DataFrame(all_records)
            
            # 数据类型转换
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce')
            
            # 删除无效数据
            df = df.dropna(subset=['Date', 'Cost'])
            
            # 按日期排序
            df = df.sort_values('Date')
            
            logger.info(f"解析阿里云费用数据完成: {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"解析阿里云费用数据失败: {e}")
            return pd.DataFrame()
    
    def analyze_costs_by_service(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        按服务分析费用
        
        Args:
            df: 费用数据DataFrame
            
        Returns:
            服务费用统计DataFrame
        """
        if df.empty:
            return pd.DataFrame()
        
        try:
            # 按服务聚合
            service_stats = df.groupby('Service').agg({
                'Cost': ['sum', 'mean', 'count']
            }).round(4)
            
            # 重命名列
            service_stats.columns = ['总费用', '平均费用', '记录数']
            
            # 按总费用降序排序
            service_stats = service_stats.sort_values('总费用', ascending=False)
            
            logger.info(f"阿里云服务费用分析完成: {len(service_stats)} 个服务")
            return service_stats
            
        except Exception as e:
            logger.error(f"阿里云服务费用分析失败: {e}")
            return pd.DataFrame()
    
    def analyze_costs_by_region(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        按区域分析费用
        
        Args:
            df: 费用数据DataFrame
            
        Returns:
            区域费用统计DataFrame
        """
        if df.empty:
            return pd.DataFrame()
        
        try:
            # 按区域聚合
            region_stats = df.groupby('Region').agg({
                'Cost': ['sum', 'mean', 'count']
            }).round(4)
            
            # 重命名列
            region_stats.columns = ['总费用', '平均费用', '记录数']
            
            # 按总费用降序排序
            region_stats = region_stats.sort_values('总费用', ascending=False)
            
            logger.info(f"阿里云区域费用分析完成: {len(region_stats)} 个区域")
            return region_stats
            
        except Exception as e:
            logger.error(f"阿里云区域费用分析失败: {e}")
            return pd.DataFrame()
    
    def get_cost_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        获取费用摘要
        
        Args:
            df: 费用数据DataFrame
            
        Returns:
            费用摘要字典
        """
        if df.empty:
            return {
                'total_cost': 0,
                'avg_daily_cost': 0,
                'max_daily_cost': 0,
                'min_daily_cost': 0,
                'record_count': 0,
                'date_range': 0,
                'currency': 'CNY'
            }
        
        try:
            # 按日期聚合费用
            daily_costs = df.groupby('Date')['Cost'].sum()
            
            total_cost = df['Cost'].sum()
            avg_daily_cost = daily_costs.mean()
            max_daily_cost = daily_costs.max()
            min_daily_cost = daily_costs.min()
            record_count = len(df)
            date_range = (df['Date'].max() - df['Date'].min()).days + 1
            currency = df['Currency'].iloc[0] if not df.empty else 'CNY'
            
            return {
                'total_cost': round(total_cost, 2),
                'avg_daily_cost': round(avg_daily_cost, 2),
                'max_daily_cost': round(max_daily_cost, 2),
                'min_daily_cost': round(min_daily_cost, 2),
                'record_count': record_count,
                'date_range': date_range,
                'currency': currency
            }
            
        except Exception as e:
            logger.error(f"阿里云费用摘要计算失败: {e}")
            return {
                'total_cost': 0,
                'avg_daily_cost': 0,
                'max_daily_cost': 0,
                'min_daily_cost': 0,
                'record_count': 0,
                'date_range': 0,
                'currency': 'CNY'
            }
    
    def calculate_cost_trend(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        计算费用趋势
        
        Args:
            df: 费用数据DataFrame
            
        Returns:
            费用趋势数据
        """
        if df.empty:
            return {'trend': 'stable', 'change_rate': 0, 'daily_costs': []}
        
        try:
            # 按日期聚合费用
            daily_costs = df.groupby('Date')['Cost'].sum().sort_index()
            
            if len(daily_costs) < 2:
                return {'trend': 'stable', 'change_rate': 0, 'daily_costs': daily_costs.tolist()}
            
            # 计算趋势
            first_half = daily_costs[:len(daily_costs)//2].mean()
            second_half = daily_costs[len(daily_costs)//2:].mean()
            
            if second_half > first_half * 1.1:
                trend = 'increasing'
            elif second_half < first_half * 0.9:
                trend = 'decreasing'
            else:
                trend = 'stable'
            
            change_rate = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0
            
            return {
                'trend': trend,
                'change_rate': round(change_rate, 2),
                'daily_costs': daily_costs.tolist()
            }
            
        except Exception as e:
            logger.error(f"阿里云费用趋势计算失败: {e}")
            return {'trend': 'stable', 'change_rate': 0, 'daily_costs': []}
    
    def get_top_services(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        获取费用最高的服务
        
        Args:
            df: 费用数据DataFrame
            top_n: 返回前N个服务
            
        Returns:
            费用最高的服务DataFrame
        """
        if df.empty:
            return pd.DataFrame()
        
        try:
            service_costs = df.groupby('Service')['Cost'].sum().sort_values(ascending=False)
            return service_costs.head(top_n).to_frame('总费用')
            
        except Exception as e:
            logger.error(f"获取阿里云热门服务失败: {e}")
            return pd.DataFrame()
    
    def get_top_regions(self, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        获取费用最高的区域
        
        Args:
            df: 费用数据DataFrame
            top_n: 返回前N个区域
            
        Returns:
            费用最高的区域DataFrame
        """
        if df.empty:
            return pd.DataFrame()
        
        try:
            region_costs = df.groupby('Region')['Cost'].sum().sort_values(ascending=False)
            return region_costs.head(top_n).to_frame('总费用')
            
        except Exception as e:
            logger.error(f"获取阿里云热门区域失败: {e}")
            return pd.DataFrame()
