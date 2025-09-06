"""
阿里云客户端模块
"""
import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from alibabacloud_bss20140714.client import Client as BssClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_bss20140714 import models as bss_models
from alibabacloud_tea_util import models as util_models

from ..utils.logger import get_logger
from ..utils.exceptions import AWSAnalyzerError

logger = get_logger()


class AliyunClient:
    """阿里云费用分析客户端"""
    
    def __init__(self, access_key_id: Optional[str] = None, access_key_secret: Optional[str] = None, region: str = 'cn-hangzhou'):
        """
        初始化阿里云客户端
        
        Args:
            access_key_id: 阿里云AccessKey ID
            access_key_secret: 阿里云AccessKey Secret
            region: 阿里云区域
        """
        self.region = region
        self.access_key_id = access_key_id or os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
        self.access_key_secret = access_key_secret or os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
        
        if not self.access_key_id or not self.access_key_secret:
            logger.warning("阿里云凭证未配置，将跳过阿里云费用分析")
            self.client = None
            return
        
        try:
            # 创建配置
            config = open_api_models.Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret,
                region_id=self.region,
                endpoint='business.aliyuncs.com'
            )
            
            # 创建BSS客户端
            self.client = BssClient(config)
            logger.info(f"阿里云客户端初始化成功 - Region: {self.region}")
            
        except Exception as e:
            logger.error(f"阿里云客户端初始化失败: {e}")
            self.client = None
    
    def test_connection(self) -> tuple[bool, str]:
        """测试阿里云连接"""
        if not self.client:
            return False, "阿里云凭证未配置"
        
        try:
            # 尝试调用一个简单的API来测试连接
            request = bss_models.QueryAccountBalanceRequest()
            runtime = util_models.RuntimeOptions()
            
            response = self.client.query_account_balance_with_options(request, runtime)
            if response.status_code == 200:
                return True, f"阿里云连接成功 - 账户余额: {response.body.data.available_amount} 元"
            else:
                return False, f"阿里云连接失败 - 状态码: {response.status_code}"
                
        except Exception as e:
            return False, f"阿里云连接测试失败: {str(e)}"
    
    def get_billing_data(self, start_date: str, end_date: str, granularity: str = 'MONTHLY') -> Optional[Dict[str, Any]]:
        """
        获取阿里云账单数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            granularity: 数据粒度 (MONTHLY, DAILY)
            
        Returns:
            账单数据字典
        """
        if not self.client:
            logger.warning("阿里云客户端未初始化，跳过数据获取")
            return None
        
        try:
            logger.info(f"获取阿里云账单数据: {start_date} 到 {end_date}")
            
            # 查询账单概览
            request = bss_models.QueryBillOverviewRequest(
                billing_cycle=start_date[:7].replace('-', ''),  # YYYYMM格式
                granularity=granularity
            )
            
            runtime = util_models.RuntimeOptions()
            response = self.client.query_bill_overview_with_options(request, runtime)
            
            if response.status_code != 200:
                logger.error(f"阿里云API调用失败 - 状态码: {response.status_code}")
                return None
            
            return {
                'billing_data': response.body.data,
                'request_id': response.body.request_id,
                'success': response.body.success
            }
            
        except Exception as e:
            logger.error(f"获取阿里云账单数据失败: {e}")
            return None
    
    def get_instance_billing_data(self, start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取实例级别的账单数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            实例账单数据列表
        """
        if not self.client:
            logger.warning("阿里云客户端未初始化，跳过实例数据获取")
            return None
        
        try:
            logger.info(f"获取阿里云实例账单数据: {start_date} 到 {end_date}")
            
            # 按月获取数据
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            all_instances = []
            current_dt = start_dt
            
            while current_dt <= end_dt:
                billing_cycle = current_dt.strftime('%Y%m')
                
                request = bss_models.QueryInstanceBillRequest(
                    billing_cycle=billing_cycle,
                    page_num=1,
                    page_size=300  # 每页最多300条记录
                )
                
                runtime = util_models.RuntimeOptions()
                response = self.client.query_instance_bill_with_options(request, runtime)
                
                if response.status_code == 200 and response.body.data:
                    instances = response.body.data.items
                    if instances:
                        all_instances.extend([{
                            'instance_id': item.instance_id,
                            'instance_name': getattr(item, 'instance_name', ''),
                            'product_name': item.product_name,
                            'product_type': getattr(item, 'product_type', ''),
                            'subscription_type': item.subscription_type,
                            'region': getattr(item, 'region', ''),
                            'zone': getattr(item, 'zone', ''),
                            'pretax_amount': float(item.pretax_amount or 0),
                            'currency': getattr(item, 'currency', 'CNY'),
                            'billing_date': item.billing_date,
                            'usage_start_time': getattr(item, 'usage_start_time', ''),
                            'usage_end_time': getattr(item, 'usage_end_time', ''),
                        } for item in instances])
                
                # 移动到下一个月
                current_dt = current_dt + relativedelta(months=1)
            
            logger.info(f"获取到 {len(all_instances)} 条阿里云实例账单记录")
            return all_instances
            
        except Exception as e:
            logger.error(f"获取阿里云实例账单数据失败: {e}")
            return None
    
    def get_product_billing_data(self, start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取产品级别的账单数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            产品账单数据列表
        """
        if not self.client:
            logger.warning("阿里云客户端未初始化，跳过产品数据获取")
            return None
        
        try:
            logger.info(f"获取阿里云产品账单数据: {start_date} 到 {end_date}")
            
            # 按月获取数据
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            all_products = []
            current_dt = start_dt
            
            while current_dt <= end_dt:
                billing_cycle = current_dt.strftime('%Y%m')
                
                request = bss_models.QueryBillRequest(
                    billing_cycle=billing_cycle,
                    page_num=1,
                    page_size=300,
                    granularity='MONTHLY'
                )
                
                runtime = util_models.RuntimeOptions()
                response = self.client.query_bill_with_options(request, runtime)
                
                if response.status_code == 200 and response.body.data:
                    items = response.body.data.items
                    if items:
                        all_products.extend([{
                            'product_name': item.product_name,
                            'product_code': item.product_code,
                            'product_type': getattr(item, 'product_type', ''),
                            'subscription_type': item.subscription_type,
                            'pretax_amount': float(item.pretax_amount or 0),
                            'currency': getattr(item, 'currency', 'CNY'),
                            'billing_date': item.billing_date,
                            'account_id': getattr(item, 'owner_id', ''),
                            'account_name': getattr(item, 'account_name', ''),
                        } for item in items])
                
                # 移动到下一个月
                current_dt = current_dt + relativedelta(months=1)
            
            logger.info(f"获取到 {len(all_products)} 条阿里云产品账单记录")
            return all_products
            
        except Exception as e:
            logger.error(f"获取阿里云产品账单数据失败: {e}")
            return None
    
    def get_cost_and_usage_with_retry(self, start_date: str, end_date: str, granularity: str = 'MONTHLY', max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        带重试机制的费用数据获取
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            granularity: 数据粒度
            max_retries: 最大重试次数
            
        Returns:
            费用数据字典
        """
        for attempt in range(max_retries):
            try:
                # 获取实例级别和产品级别的数据
                instance_data = self.get_instance_billing_data(start_date, end_date)
                product_data = self.get_product_billing_data(start_date, end_date)
                
                return {
                    'instance_data': instance_data or [],
                    'product_data': product_data or [],
                    'start_date': start_date,
                    'end_date': end_date,
                    'granularity': granularity,
                    'provider': 'aliyun'
                }
                
            except Exception as e:
                logger.warning(f"阿里云费用数据获取失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"阿里云费用数据获取最终失败: {e}")
                    return None
        
        return None
