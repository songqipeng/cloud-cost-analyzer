"""
火山云数据处理模块
"""
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger()


class VolcengineDataProcessor:
    """火山云费用数据处理器"""
    
    def __init__(self, cost_threshold: float = 0.01):
        """
        初始化数据处理器
        
        Args:
            cost_threshold: 费用过滤阈值
        """
        self.cost_threshold = cost_threshold
    
    def parse_cost_data(self, cost_data: Dict[str, Any]) -> pd.DataFrame:
        """
        解析火山云费用数据
        
        Args:
            cost_data: 火山云费用数据
            
        Returns:
            解析后的DataFrame
        """
        if not cost_data:
            logger.warning("火山云费用数据为空")
            return pd.DataFrame()
        
        try:
            all_records = []
            
            # 处理费用汇总数据
            summary_data = cost_data.get('summary_data', [])
            for item in summary_data:
                record = {
                    'Date': item.get('month', '') + '-01',  # 转换为日期格式
                    'Service': item.get('product_name', 'Unknown'),
                    'Region': 'Unknown',  # 火山云汇总数据通常没有区域信息
                    'Cost': float(item.get('total_cost', 0)),
                    'Currency': item.get('currency', 'CNY'),
                    'Provider': 'volcengine',
                    'ProductCode': item.get('product_code', ''),
                    'OriginalCost': float(item.get('original_cost', 0)),
                    'DiscountAmount': float(item.get('discount_amount', 0))
                }
                
                # 过滤低于阈值的费用
                if record['Cost'] >= self.cost_threshold:
                    all_records.append(record)
            
            if not all_records:
                logger.warning("没有找到符合条件的火山云费用记录")
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
            
            logger.info(f"解析火山云费用数据完成: {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"解析火山云费用数据失败: {e}")
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
            
            logger.info(f"火山云服务费用分析完成: {len(service_stats)} 个服务")
            return service_stats
            
        except Exception as e:
            logger.error(f"火山云服务费用分析失败: {e}")
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
            
            logger.info(f"火山云区域费用分析完成: {len(region_stats)} 个区域")
            return region_stats
            
        except Exception as e:
            logger.error(f"火山云区域费用分析失败: {e}")
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
            logger.error(f"火山云费用摘要计算失败: {e}")
            return {
                'total_cost': 0,
                'avg_daily_cost': 0,
                'max_daily_cost': 0,
                'min_daily_cost': 0,
                'record_count': 0,
                'date_range': 0,
                'currency': 'CNY'
            }
