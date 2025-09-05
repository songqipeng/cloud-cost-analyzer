"""
AWS客户端模块
"""
import boto3
from typing import Optional, Dict, Any, List, Tuple
from botocore.exceptions import ClientError, NoCredentialsError
from ..utils.validators import DataValidator
from ..utils.exceptions import AWSConnectionError, AWSConfigError
from ..utils.logger import get_logger

logger = get_logger()


class AWSClient:
    """AWS客户端封装类"""
    
    def __init__(self, profile: Optional[str] = None, region: str = 'us-east-1'):
        """
        初始化AWS客户端
        
        Args:
            profile: AWS配置文件名称
            region: AWS区域
        """
        self.profile = profile
        self.region = region
        self.session = None
        self.ce_client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """初始化AWS客户端"""
        try:
            logger.info(f"初始化AWS客户端 - Profile: {self.profile}, Region: {self.region}")
            self.session = boto3.Session(profile_name=self.profile)
            self.ce_client = self.session.client('ce', region_name=self.region)
            logger.info("AWS客户端初始化成功")
        except Exception as e:
            logger.error(f"AWS客户端初始化失败: {e}")
            raise AWSConnectionError(f"AWS客户端初始化失败: {e}")
    
    def validate_credentials(self) -> Tuple[bool, Optional[str]]:
        """验证AWS凭证"""
        return DataValidator.validate_aws_credentials(self.profile)
    
    def validate_cost_explorer_permissions(self) -> Tuple[bool, Optional[str]]:
        """验证Cost Explorer API权限"""
        return DataValidator.validate_cost_explorer_permissions(self.profile)
    
    def get_cost_and_usage(
        self,
        start_date: str,
        end_date: str,
        granularity: str = 'MONTHLY',
        group_by: Optional[List[Dict[str, str]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取费用和使用情况数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            granularity: 数据粒度 (DAILY, MONTHLY)
            group_by: 分组维度
            
        Returns:
            费用数据字典或None
        """
        # 验证日期格式
        is_valid, error_msg = DataValidator.validate_date_range(start_date, end_date)
        if not is_valid:
            raise ValueError(error_msg)
        
        # 默认分组
        if group_by is None:
            group_by = [
                {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                {'Type': 'DIMENSION', 'Key': 'REGION'}
            ]
        
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity=granularity,
                Metrics=['UnblendedCost'],
                GroupBy=group_by
            )
            return response
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS API错误: {error_code} - {error_message}")
            
            if error_code == 'AccessDenied':
                raise AWSConnectionError("缺少Cost Explorer API访问权限")
            elif error_code == 'ThrottlingException':
                raise AWSConnectionError("API调用频率过高，请稍后重试")
            elif error_code == 'InvalidParameterValue':
                raise AWSConfigError(f"参数值无效: {error_message}")
            else:
                raise AWSConnectionError(f"获取费用数据失败: {error_code} - {error_message}")
        except Exception as e:
            logger.error(f"获取费用数据异常: {e}")
            raise AWSConnectionError(f"获取费用数据异常: {e}")
    
    def get_cost_and_usage_with_retry(
        self,
        start_date: str,
        end_date: str,
        granularity: str = 'MONTHLY',
        max_retries: int = 3,
        retry_delay: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        带重试机制的费用数据获取
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            granularity: 数据粒度
            max_retries: 最大重试次数
            retry_delay: 重试延迟(秒)
            
        Returns:
            费用数据字典或None
        """
        import time
        
        for attempt in range(max_retries):
            try:
                return self.get_cost_and_usage(start_date, end_date, granularity)
            except Exception as e:
                if "ThrottlingException" in str(e) and attempt < max_retries - 1:
                    print(f"⚠️  API限流，{retry_delay}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                    continue
                else:
                    raise e
        
        return None
    
    def get_account_info(self) -> Dict[str, Any]:
        """获取账户信息"""
        try:
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            return {
                'account_id': identity.get('Account'),
                'user_id': identity.get('UserId'),
                'arn': identity.get('Arn')
            }
        except Exception as e:
            raise Exception(f"获取账户信息失败: {e}")
    
    def test_connection(self) -> Tuple[bool, str]:
        """测试AWS连接"""
        try:
            # 验证凭证
            is_valid, error_msg = self.validate_credentials()
            if not is_valid:
                return False, f"凭证验证失败: {error_msg}"
            
            # 验证Cost Explorer权限
            has_permission, error_msg = self.validate_cost_explorer_permissions()
            if not has_permission:
                return False, f"权限验证失败: {error_msg}"
            
            # 获取账户信息
            account_info = self.get_account_info()
            
            return True, f"连接成功 - 账户ID: {account_info['account_id']}"
        except Exception as e:
            return False, f"连接测试失败: {e}"
