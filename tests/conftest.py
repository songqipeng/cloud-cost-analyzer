"""
测试配置和共享fixture
"""
import pytest
from unittest.mock import Mock, MagicMock
import os
import json
from datetime import datetime, date
from typing import Dict, Any


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Mock配置数据"""
    return {
        "aws": {
            "default_region": "us-east-1",
            "cost_threshold": 0.01
        },
        "aliyun": {
            "enabled": True,
            "default_region": "cn-hangzhou",
            "access_key_id": "test_key",
            "access_key_secret": "test_secret",
            "cost_threshold": 0.01
        },
        "tencent": {
            "enabled": True,
            "default_region": "ap-beijing",
            "secret_id": "test_id",
            "secret_key": "test_key",
            "cost_threshold": 0.01
        },
        "volcengine": {
            "enabled": True,
            "default_region": "cn-beijing",
            "access_key_id": "test_key",
            "secret_access_key": "test_secret",
            "cost_threshold": 0.01
        },
        "notifications": {
            "email": {
                "enabled": False
            },
            "feishu": {
                "enabled": False
            }
        }
    }


@pytest.fixture
def mock_aws_cost_data():
    """Mock AWS费用数据"""
    return {
        'ResultsByTime': [
            {
                'TimePeriod': {
                    'Start': '2024-01-01',
                    'End': '2024-01-02'
                },
                'Total': {
                    'UnblendedCost': {
                        'Amount': '12.34',
                        'Unit': 'USD'
                    }
                },
                'Groups': [
                    {
                        'Keys': ['EC2-Instance'],
                        'Metrics': {
                            'UnblendedCost': {
                                'Amount': '8.50',
                                'Unit': 'USD'
                            }
                        }
                    },
                    {
                        'Keys': ['S3'],
                        'Metrics': {
                            'UnblendedCost': {
                                'Amount': '3.84',
                                'Unit': 'USD'
                            }
                        }
                    }
                ]
            }
        ]
    }


@pytest.fixture
def mock_aliyun_cost_data():
    """Mock阿里云费用数据"""
    return {
        'Code': '200',
        'Data': {
            'Items': {
                'Item': [
                    {
                        'BillingDate': '2024-01-01',
                        'ProductCode': 'ecs',
                        'ProductName': 'Elastic Compute Service',
                        'PretaxAmount': 45.67,
                        'Currency': 'CNY'
                    },
                    {
                        'BillingDate': '2024-01-01', 
                        'ProductCode': 'oss',
                        'ProductName': 'Object Storage Service',
                        'PretaxAmount': 12.34,
                        'Currency': 'CNY'
                    }
                ]
            }
        }
    }


@pytest.fixture
def mock_tencent_cost_data():
    """Mock腾讯云费用数据"""
    return {
        'Response': {
            'DetailSet': [
                {
                    'Date': '2024-01-01',
                    'ProductCode': 'cvm',
                    'ProductCodeName': '云服务器CVM',
                    'PayerAmount': '89.12',
                    'Currency': 'CNY'
                },
                {
                    'Date': '2024-01-01',
                    'ProductCode': 'cos',
                    'ProductCodeName': '对象存储COS',
                    'PayerAmount': '23.45',
                    'Currency': 'CNY'
                }
            ]
        }
    }


@pytest.fixture
def mock_volcengine_cost_data():
    """Mock火山云费用数据"""
    return {
        'Result': {
            'List': [
                {
                    'BillDate': '2024-01-01',
                    'Product': 'ECS',
                    'ProductName': '云服务器',
                    'BillAmount': 67.89,
                    'Currency': 'CNY'
                },
                {
                    'BillDate': '2024-01-01',
                    'Product': 'TOS',
                    'ProductName': '对象存储',
                    'BillAmount': 15.67,
                    'Currency': 'CNY'
                }
            ]
        }
    }


@pytest.fixture
def mock_boto3_client():
    """Mock boto3客户端"""
    mock_client = Mock()
    mock_client.get_caller_identity.return_value = {
        'Account': '123456789012',
        'UserId': 'AIDACKCEVSQ6C2EXAMPLE',
        'Arn': 'arn:aws:iam::123456789012:user/test-user'
    }
    return mock_client


@pytest.fixture
def mock_environment_variables(monkeypatch):
    """设置测试环境变量"""
    test_env = {
        'AWS_ACCESS_KEY_ID': 'AKIATEST123456789',
        'AWS_SECRET_ACCESS_KEY': 'test-secret-key',
        'ALIBABA_CLOUD_ACCESS_KEY_ID': 'LTAI_test_key',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'test_secret',
        'TENCENTCLOUD_SECRET_ID': 'AKIDtest123456',
        'TENCENTCLOUD_SECRET_KEY': 'test_secret_key',
        'VOLCENGINE_ACCESS_KEY_ID': 'AKLT_test_key',
        'VOLCENGINE_SECRET_ACCESS_KEY': 'test_secret_key'
    }
    
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def temp_config_file(tmp_path):
    """创建临时配置文件"""
    config_file = tmp_path / "config.json"
    config_data = {
        "aws": {
            "default_region": "us-east-1",
            "cost_threshold": 0.01
        },
        "notifications": {
            "email": {"enabled": False},
            "feishu": {"enabled": False}
        }
    }
    config_file.write_text(json.dumps(config_data, indent=2))
    return str(config_file)


class MockDatetime:
    """Mock datetime类用于测试"""
    @classmethod
    def now(cls):
        return datetime(2024, 1, 15, 10, 30, 0)
    
    @classmethod
    def today(cls):
        return date(2024, 1, 15)


@pytest.fixture
def mock_datetime(monkeypatch):
    """Mock datetime"""
    monkeypatch.setattr('datetime.datetime', MockDatetime)
    monkeypatch.setattr('datetime.date', MockDatetime)