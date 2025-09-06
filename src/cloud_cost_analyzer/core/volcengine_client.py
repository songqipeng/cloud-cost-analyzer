"""
火山云客户端模块
"""
import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

try:
    from volcengine.core.session import Session
    from volcengine.billing import BillingService
    VOLCENGINE_AVAILABLE = True
except ImportError:
    VOLCENGINE_AVAILABLE = False

from ..utils.logger import get_logger
from ..utils.exceptions import AWSAnalyzerError

logger = get_logger()


class VolcengineClient:
    """火山云费用分析客户端"""
    
    def __init__(self, access_key_id: Optional[str] = None, secret_access_key: Optional[str] = None, region: str = 'cn-beijing'):
        """
        初始化火山云客户端
        
        Args:
            access_key_id: 火山云AccessKeyId
            secret_access_key: 火山云SecretAccessKey
            region: 火山云区域
        """
        self.region = region
        self.access_key_id = access_key_id or os.getenv('VOLCENGINE_ACCESS_KEY_ID')
        self.secret_access_key = secret_access_key or os.getenv('VOLCENGINE_SECRET_ACCESS_KEY')
        
        if not VOLCENGINE_AVAILABLE:
            logger.warning("火山云SDK未安装，将跳过火山云费用分析")
            self.client = None
            return
        
        if not self.access_key_id or not self.secret_access_key:
            logger.warning("火山云凭证未配置，将跳过火山云费用分析")
            self.client = None
            return
        
        try:
            # 创建会话
            session = Session(
                ak=self.access_key_id,
                sk=self.secret_access_key,
                region=self.region
            )
            
            # 创建计费服务客户端
            self.client = BillingService(session)
            logger.info(f"火山云客户端初始化成功 - Region: {self.region}")
            
        except Exception as e:
            logger.error(f"火山云客户端初始化失败: {e}")
            self.client = None
    
    def test_connection(self) -> tuple[bool, str]:
        """测试火山云连接"""
        if not self.client:
            return False, "火山云凭证未配置"
        
        try:
            # 尝试调用账户余额API来测试连接
            response = self.client.query_account_balance()
            
            if response and 'Result' in response:
                balance_info = response['Result']
                available_balance = balance_info.get('AvailableBalance', 0)
                return True, f"火山云连接成功 - 可用余额: {available_balance:.2f} 元"
            else:
                return True, "火山云连接成功"
                
        except Exception as e:
            return False, f"火山云连接测试失败: {str(e)}"
    
    def get_billing_data(self, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """
        获取火山云账单数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            账单数据字典
        """
        if not self.client:
            logger.warning("火山云客户端未初始化，跳过数据获取")
            return None
        
        try:
            logger.info(f"获取火山云账单数据: {start_date} 到 {end_date}")
            
            # 查询账单明细
            params = {
                'BillPeriod': start_date[:7].replace('-', ''),  # YYYYMM格式
                'Limit': 100,
                'Offset': 0
            }
            
            all_details = []
            
            while True:
                response = self.client.list_bill_detail(params)
                
                if response and 'Result' in response:
                    result = response['Result']
                    details = result.get('List', [])
                    
                    if details:
                        all_details.extend(details)
                        
                        # 检查是否还有更多数据
                        if len(details) < params['Limit']:
                            break
                        params['Offset'] += params['Limit']
                    else:
                        break
                else:
                    break
            
            return {
                'billing_data': all_details,
                'request_id': response.get('ResponseMetadata', {}).get('RequestId', ''),
                'total_count': len(all_details)
            }
            
        except Exception as e:
            logger.error(f"获取火山云账单数据失败: {e}")
            return None
    
    def get_cost_summary_data(self, start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取费用汇总数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            费用汇总数据列表
        """
        if not self.client:
            logger.warning("火山云客户端未初始化，跳过汇总数据获取")
            return None
        
        try:
            logger.info(f"获取火山云费用汇总数据: {start_date} 到 {end_date}")
            
            # 按月获取数据
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            all_summary = []
            current_dt = start_dt
            
            while current_dt <= end_dt:
                bill_period = current_dt.strftime('%Y%m')
                
                # 查询月度费用汇总
                params = {
                    'BillPeriod': bill_period,
                    'GroupBy': ['Product'],
                    'Limit': 100,
                    'Offset': 0
                }
                
                try:
                    response = self.client.list_bill_overview_by_product(params)
                    
                    if response and 'Result' in response:
                        result = response['Result']
                        overview_list = result.get('List', [])
                        
                        for item in overview_list:
                            all_summary.append({
                                'month': current_dt.strftime('%Y-%m'),
                                'product_name': item.get('Product', 'Unknown'),
                                'product_code': item.get('ProductCode', ''),
                                'total_cost': float(item.get('PayableAmount', 0)),
                                'original_cost': float(item.get('OriginalBillAmount', 0)),
                                'discount_amount': float(item.get('DiscountBillAmount', 0)),
                                'currency': 'CNY'
                            })
                
                except Exception as e:
                    logger.warning(f"获取火山云 {bill_period} 月费用汇总失败: {e}")
                
                # 移动到下一个月
                current_dt = current_dt + relativedelta(months=1)
            
            logger.info(f"获取到 {len(all_summary)} 条火山云费用汇总记录")
            return all_summary
            
        except Exception as e:
            logger.error(f"获取火山云费用汇总数据失败: {e}")
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
                # 获取费用汇总数据
                summary_data = self.get_cost_summary_data(start_date, end_date)
                
                return {
                    'summary_data': summary_data or [],
                    'start_date': start_date,
                    'end_date': end_date,
                    'granularity': granularity,
                    'provider': 'volcengine'
                }
                
            except Exception as e:
                logger.warning(f"火山云费用数据获取失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"火山云费用数据获取最终失败: {e}")
                    return None
        
        return None
