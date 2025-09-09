#!/usr/bin/env python3
"""
测试安全日志和敏感信息脱敏功能
"""
import sys
import os
import json

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from cloud_cost_analyzer.utils.secure_logger import (
    get_secure_logger, 
    mask_sensitive_data, 
    SensitiveDataMasker
)

def test_sensitive_data_masking():
    """测试敏感信息脱敏功能"""
    print("🔐 测试敏感信息脱敏功能...")
    
    masker = SensitiveDataMasker()
    
    # 测试各种敏感信息
    sensitive_texts = [
        "AWS Access Key: AKIAIOSFODNN7EXAMPLE",
        "Secret Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", 
        "Email: user@example.com, Phone: 13812345678",
        "Aliyun Key: LTAI5tFhPQR7YzPqVUVgWxYz",
        "Tencent ID: AKIDQjz3ltompVjBabyYu5nS",
        "User password is: MySecretPass123!",
        "Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIi",
        "Bank card: 6222021234567890123"
    ]
    
    print("\n1. 文本脱敏测试")
    for i, text in enumerate(sensitive_texts, 1):
        masked = masker.mask_text(text)
        print(f"   {i}. 原文: {text}")
        print(f"      脱敏: {masked}")
        print()
    
    # 测试字典脱敏
    print("2. 字典脱敏测试")
    sensitive_dict = {
        "aws_access_key": "AKIAIOSFODNN7EXAMPLE",
        "aws_secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "user_info": {
            "email": "user@company.com",
            "phone": "13812345678",
            "name": "张三"
        },
        "config": {
            "password": "MyPassword123",
            "token": "Bearer eyJhbGciOiJIUzI1NiIs",
            "normal_field": "这是正常字段"
        },
        "cloud_credentials": [
            {
                "provider": "aliyun", 
                "access_key_id": "LTAI5tFhPQR7YzPqVUVgWxYz",
                "secret": "very_secret_key_value"
            }
        ]
    }
    
    print("   原始数据:")
    print(f"   {json.dumps(sensitive_dict, indent=2, ensure_ascii=False)}")
    
    masked_dict = masker.mask_dict(sensitive_dict)
    print("\n   脱敏后数据:")
    print(f"   {json.dumps(masked_dict, indent=2, ensure_ascii=False)}")
    
    return True

def test_secure_logging():
    """测试安全日志功能"""
    print("\n🔍 测试安全日志系统...")
    
    # 创建安全日志器
    logger = get_secure_logger('test_logger')
    
    print("\n1. 基本日志记录测试")
    logger.info("这是一条普通的信息日志")
    logger.warning("这是一条警告日志")
    
    print("\n2. 敏感信息自动脱敏测试")
    
    # 测试字符串日志脱敏
    logger.info("AWS密钥: AKIAIOSFODNN7EXAMPLE, 用户邮箱: admin@company.com")
    
    # 测试字典日志脱敏
    config_data = {
        "aws": {
            "access_key": "AKIAIOSFODNN7EXAMPLE",
            "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        },
        "user": {
            "email": "user@example.com",
            "phone": "13812345678"
        }
    }
    logger.info(f"配置信息: {config_data}")
    
    print("\n3. 审计日志测试")
    logger.audit(
        action="cost_analysis",
        details={
            "provider": "aws", 
            "access_key": "AKIAIOSFODNN7EXAMPLE",
            "total_cost": 123.45,
            "user_email": "analyst@company.com"
        },
        user_id="user123",
        result="SUCCESS"
    )
    
    print("\n4. API调用日志测试")
    logger.log_api_call(
        provider="aws",
        operation="get_cost_data",
        duration=2.5,
        success=True
    )
    
    logger.log_api_call(
        provider="aliyun", 
        operation="get_cost_data",
        duration=1.2,
        success=False,
        error_message="认证失败: 密钥 LTAI5tFhPQR7YzPqVUVgWxYz 无效"
    )
    
    print("\n5. 成本分析日志测试")
    logger.log_cost_analysis(
        provider="aws",
        date_range="2024-01-01 to 2024-01-31", 
        total_cost=1234.56,
        service_count=5
    )
    
    # 获取日志器统计信息
    print("\n6. 日志器统计信息")
    stats = logger.get_log_stats()
    print(f"   日志器名称: {stats['logger_name']}")
    print(f"   日志级别: {stats['log_level']}")
    print(f"   处理器数量: {stats['handlers_count']}")
    
    for i, handler_info in enumerate(stats['handlers'], 1):
        print(f"   处理器{i}: {handler_info['type']} (级别: {handler_info['level']})")
        if 'file' in handler_info:
            print(f"     文件: {handler_info['file']}")
    
    return True

def test_masking_performance():
    """测试脱敏性能"""
    print("\n⚡ 脱敏性能测试...")
    
    import time
    
    masker = SensitiveDataMasker()
    
    # 创建测试数据
    test_text = """
    配置信息包含以下内容:
    AWS Access Key: AKIAIOSFODNN7EXAMPLE
    AWS Secret: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    用户邮箱: user@company.com
    联系电话: 13812345678
    阿里云密钥: LTAI5tFhPQR7YzPqVUVgWxYz
    腾讯云ID: AKIDQjz3ltompVjBabyYu5nS
    """
    
    # 性能测试
    start_time = time.time()
    iterations = 1000
    
    for _ in range(iterations):
        masked = masker.mask_text(test_text)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"   处理 {iterations} 次文本脱敏")
    print(f"   总耗时: {duration:.4f}秒")
    print(f"   平均耗时: {duration/iterations*1000:.2f}毫秒/次")
    print(f"   处理速度: {iterations/duration:.0f}次/秒")
    
    return True

if __name__ == '__main__':
    try:
        print("🔐 安全日志和脱敏功能测试")
        print("=" * 50)
        
        test_sensitive_data_masking()
        test_secure_logging() 
        test_masking_performance()
        
        print("\n✅ 安全日志测试完成!")
        
        # 检查是否生成了日志文件
        if os.path.exists('logs'):
            print(f"\n📁 日志文件已生成:")
            for file in os.listdir('logs'):
                file_path = os.path.join('logs', file)
                file_size = os.path.getsize(file_path)
                print(f"   {file} ({file_size} bytes)")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()