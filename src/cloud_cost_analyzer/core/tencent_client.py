"""
腾讯云客户端模块
"""
import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

try:
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.billing.v20180709 import billing_client, models as billing_models
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    TENCENT_AVAILABLE = True
except ImportError:
    TENCENT_AVAILABLE = False

from ..utils.logger import get_logger
from ..utils.exceptions import AWSAnalyzerError

logger = get_logger()


class TencentClient:
    """腾讯云费用分析客户端"""
    
    def __init__(self, secret_id: Optional[str] = None, secret_key: Optional[str] = None, region: str = 'ap-beijing'):
        """
        初始化腾讯云客户端
        
        Args:
            secret_id: 腾讯云SecretId
            secret_key: 腾讯云SecretKey
            region: 腾讯云区域
        """
        self.region = region
        self.secret_id = secret_id or os.getenv('TENCENTCLOUD_SECRET_ID')
        self.secret_key = secret_key or os.getenv('TENCENTCLOUD_SECRET_KEY')
        
        if not TENCENT_AVAILABLE:
            logger.warning("腾讯云SDK未安装，将跳过腾讯云费用分析")
            self.client = None
            return
        
        if not self.secret_id or not self.secret_key:
            logger.warning("腾讯云凭证未配置，将跳过腾讯云费用分析")
            self.client = None
            return
        
        try:
            # 创建凭证对象
            cred = credential.Credential(self.secret_id, self.secret_key)
            
            # 创建HTTP配置
            http_profile = HttpProfile()
            http_profile.endpoint = "billing.tencentcloudapi.com"
            
            # 创建客户端配置
            client_profile = ClientProfile()
            client_profile.httpProfile = http_profile
            
            # 创建计费客户端
            self.client = billing_client.BillingClient(cred, self.region, client_profile)
            logger.info(f"腾讯云客户端初始化成功 - Region: {self.region}")
            
        except Exception as e:
            logger.error(f"腾讯云客户端初始化失败: {e}")
            self.client = None
    
    def test_connection(self) -> tuple[bool, str]:
        """测试腾讯云连接"""
        if not self.client:
            return False, "腾讯云凭证未配置"
        
        try:
            # 尝试调用账户余额API来测试连接
            req = billing_models.DescribeAccountBalanceRequest()
            resp = self.client.DescribeAccountBalance(req)
            
            if resp.Balance is not None:
                balance = float(resp.Balance) / 100  # 腾讯云返回的是分，需要转换为元
                return True, f"腾讯云连接成功 - 账户余额: {balance:.2f} 元"
            else:
                return True, "腾讯云连接成功"
                
        except TencentCloudSDKException as e:
            return False, f"腾讯云连接测试失败: {e.message}"
        except Exception as e:
            return False, f"腾讯云连接测试失败: {str(e)}"
    
    def get_billing_data(self, start_date: str, end_date: str) -> Optional[Dict[str, Any]]:
        """
        获取腾讯云账单数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            账单数据字典
        """
        if not self.client:
            logger.warning("腾讯云客户端未初始化，跳过数据获取")
            return None
        
        try:
            logger.info(f"获取腾讯云账单数据: {start_date} 到 {end_date}")
            
            # 查询账单明细
            req = billing_models.DescribeBillDetailRequest()
            req.Month = start_date[:7]  # YYYY-MM格式
            req.PageSize = 100
            req.Page = 1
            
            all_details = []
            
            while True:
                resp = self.client.DescribeBillDetail(req)
                
                if resp.DetailSet:
                    all_details.extend(resp.DetailSet)
                    
                    # 检查是否还有更多数据
                    if len(resp.DetailSet) < req.PageSize:
                        break
                    req.Page += 1
                else:
                    break
            
            return {
                'billing_data': all_details,
                'request_id': getattr(resp, 'RequestId', ''),
                'total_count': len(all_details)
            }
            
        except TencentCloudSDKException as e:
            logger.error(f"获取腾讯云账单数据失败: {e.message}")
            return None
        except Exception as e:
            logger.error(f"获取腾讯云账单数据失败: {e}")
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
            logger.warning("腾讯云客户端未初始化，跳过汇总数据获取")
            return None
        
        try:
            logger.info(f"获取腾讯云费用汇总数据: {start_date} 到 {end_date}")
            
            # 按月获取数据
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            
            all_summary = []
            current_dt = start_dt
            
            while current_dt <= end_dt:
                month = current_dt.strftime('%Y-%m')
                
                # 查询月度费用汇总
                req = billing_models.DescribeBillSummaryByProductRequest()
                req.Month = month
                req.PayerUin = ""  # 空表示查询当前账号
                
                try:
                    resp = self.client.DescribeBillSummaryByProduct(req)
                    
                    if resp.SummaryOverview:
                        for item in resp.SummaryOverview:
                            all_summary.append({
                                'month': month,
                                'product_name': item.BusinessCodeName,
                                'product_code': item.BusinessCode,
                                'total_cost': float(item.TotalCost or 0),
                                'real_total_cost': float(item.RealTotalCost or 0),
                                'cash_pay_amount': float(item.CashPayAmount or 0),
                                'voucher_pay_amount': float(item.VoucherPayAmount or 0),
                                'incentive_pay_amount': float(item.IncentivePayAmount or 0),
                                'currency': 'CNY'
                            })
                
                except TencentCloudSDKException as e:
                    logger.warning(f"获取腾讯云 {month} 月费用汇总失败: {e.message}")
                
                # 移动到下一个月
                current_dt = current_dt + relativedelta(months=1)
            
            logger.info(f"获取到 {len(all_summary)} 条腾讯云费用汇总记录")
            return all_summary
            
        except Exception as e:
            logger.error(f"获取腾讯云费用汇总数据失败: {e}")
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
                    'provider': 'tencent'
                }
                
            except Exception as e:
                logger.warning(f"腾讯云费用数据获取失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"腾讯云费用数据获取最终失败: {e}")
                    return None
        
        return None
