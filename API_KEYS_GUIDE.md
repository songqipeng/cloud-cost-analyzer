# 🔑 多云平台API密钥获取指南

本指南详细说明如何获取AWS、阿里云、腾讯云、火山云四个平台的API密钥，以及如何配置和使用Cloud Cost Analyzer进行费用分析。

---

## 🚀 AWS (Amazon Web Services)

### 📋 所需权限
- `ce:GetCostAndUsage` - 获取费用和使用情况
- `ce:GetDimensionValues` - 获取维度值
- `ce:GetUsageReport` - 获取使用报告
- `sts:GetCallerIdentity` - 获取调用者身份（用于连接测试）

### 🔧 获取步骤

#### 方法一：IAM用户（推荐）

1. **登录AWS控制台**
   - 访问 [AWS控制台](https://console.aws.amazon.com/)
   - 使用管理员账户登录

2. **创建IAM用户**
   ```
   服务 → IAM → 用户 → 创建用户
   - 用户名：cloud-cost-analyzer
   - 访问类型：编程访问
   ```

3. **附加权限策略**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "ce:GetCostAndUsage",
           "ce:GetDimensionValues", 
           "ce:GetUsageReport",
           "sts:GetCallerIdentity"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

4. **获取访问密钥**
   - 创建完成后下载CSV文件
   - 记录 `Access Key ID` 和 `Secret Access Key`

#### 方法二：AWS CLI配置

```bash
# 安装AWS CLI
pip install awscli

# 配置凭证
aws configure
# AWS Access Key ID: 输入你的Access Key ID
# AWS Secret Access Key: 输入你的Secret Access Key  
# Default region name: us-east-1
# Default output format: json
```

### 🔐 配置方式

#### 环境变量（推荐）
```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"
```

#### 配置文件
```json
{
  "aws": {
    "default_region": "us-east-1",
    "cost_threshold": 0.01
  }
}
```

### 📊 使用示例
```bash
# AWS费用分析
python3 cloud_cost_analyzer.py quick

# 自定义时间范围
python3 cloud_cost_analyzer.py custom --start 2024-01-01 --end 2024-12-31
```

---

## 🌟 阿里云 (Alibaba Cloud)

### 📋 所需权限
- `AliyunBSSReadOnlyAccess` - 费用中心只读权限（推荐）
- 或 `AliyunBSSFullAccess` - 费用中心完全访问权限

### 🔧 获取步骤

1. **登录阿里云控制台**
   - 访问 [阿里云控制台](https://ecs.console.aliyun.com/)

2. **创建RAM用户**
   ```
   控制台 → 访问控制RAM → 用户管理 → 创建用户
   - 登录名称：cloud-cost-analyzer
   - 访问方式：✅ 编程访问
   ```

3. **添加权限**
   ```
   用户管理 → 找到创建的用户 → 添加权限
   - 选择权限：AliyunBSSReadOnlyAccess
   ```

4. **创建AccessKey**
   ```
   用户管理 → 用户详情 → 认证管理 → 创建AccessKey
   - 保存 AccessKey ID 和 AccessKey Secret
   ```

### 🔐 配置方式

#### 环境变量（推荐）
```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID="LTAI..."
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="..."
```

#### 配置文件
```json
{
  "aliyun": {
    "enabled": true,
    "default_region": "cn-hangzhou",
    "access_key_id": "LTAI...",
    "access_key_secret": "...",
    "cost_threshold": 0.01
  }
}
```

### 📊 使用示例
```bash
# 多云分析（包含阿里云）
python3 cloud_cost_analyzer.py multi-cloud

# 检查连接
python3 cloud_cost_analyzer.py config
```

---

## 🐧 腾讯云 (Tencent Cloud)

### 📋 所需权限
- `QcloudCamReadOnlyAccess` - 访问管理只读权限
- `QcloudBillingReadOnlyAccess` - 计费只读权限

### 🔧 获取步骤

1. **登录腾讯云控制台**
   - 访问 [腾讯云控制台](https://console.cloud.tencent.com/)

2. **创建子用户**
   ```
   控制台 → 访问管理CAM → 用户 → 用户列表 → 新建用户
   - 用户类型：自定义创建
   - 用户信息：cloud-cost-analyzer
   - 访问方式：✅ 编程访问
   ```

3. **设置用户权限**
   ```
   用户列表 → 找到创建的用户 → 关联策略
   - 添加策略：QcloudBillingReadOnlyAccess
   ```

4. **创建API密钥**
   ```
   用户详情 → API密钥 → 新建密钥
   - 保存 SecretId 和 SecretKey
   ```

### 🔐 配置方式

#### 环境变量（推荐）
```bash
export TENCENTCLOUD_SECRET_ID="AKIDxxx..."
export TENCENTCLOUD_SECRET_KEY="..."
```

#### 配置文件
```json
{
  "tencent": {
    "enabled": true,
    "default_region": "ap-beijing",
    "secret_id": "AKIDxxx...",
    "secret_key": "...",
    "cost_threshold": 0.01
  }
}
```

### 📊 使用示例
```bash
# 多云分析（包含腾讯云）
python3 cloud_cost_analyzer.py multi-cloud

# 检查腾讯云连接
python3 cloud_cost_analyzer.py config
```

---

## 🌋 火山云 (Volcengine/ByteDance Cloud)

### 📋 所需权限
- `BillingFullAccess` - 计费完全访问权限
- 或 `BillingReadOnlyAccess` - 计费只读权限（推荐）

### 🔧 获取步骤

1. **登录火山云控制台**
   - 访问 [火山云控制台](https://console.volcengine.com/)

2. **创建子用户**
   ```
   控制台 → 访问控制 → 用户管理 → 创建用户
   - 用户名：cloud-cost-analyzer
   - 访问方式：✅ API访问
   ```

3. **授权用户**
   ```
   用户管理 → 找到创建的用户 → 授权
   - 添加权限：BillingReadOnlyAccess
   ```

4. **创建访问密钥**
   ```
   用户详情 → 访问密钥 → 创建访问密钥
   - 保存 Access Key ID 和 Secret Access Key
   ```

### 🔐 配置方式

#### 环境变量（推荐）
```bash
export VOLCENGINE_ACCESS_KEY_ID="AKLT..."
export VOLCENGINE_SECRET_ACCESS_KEY="..."
```

#### 配置文件
```json
{
  "volcengine": {
    "enabled": true,
    "default_region": "cn-beijing",
    "access_key_id": "AKLT...",
    "secret_access_key": "...",
    "cost_threshold": 0.01
  }
}
```

### 📊 使用示例
```bash
# 多云分析（包含火山云）
python3 cloud_cost_analyzer.py multi-cloud

# 检查火山云连接
python3 cloud_cost_analyzer.py config
```

---

## 🔧 完整配置示例

### 环境变量配置（推荐）

```bash
# AWS
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"

# 阿里云
export ALIBABA_CLOUD_ACCESS_KEY_ID="LTAI..."
export ALIBABA_CLOUD_ACCESS_KEY_SECRET="..."

# 腾讯云
export TENCENTCLOUD_SECRET_ID="AKIDxxx..."
export TENCENTCLOUD_SECRET_KEY="..."

# 火山云
export VOLCENGINE_ACCESS_KEY_ID="AKLT..."
export VOLCENGINE_SECRET_ACCESS_KEY="..."
```

### 配置文件 (config.json)

```json
{
  "aws": {
    "default_region": "us-east-1",
    "cost_threshold": 0.01
  },
  "aliyun": {
    "enabled": true,
    "default_region": "cn-hangzhou",
    "access_key_id": "",
    "access_key_secret": "",
    "cost_threshold": 0.01
  },
  "tencent": {
    "enabled": true,
    "default_region": "ap-beijing",
    "secret_id": "",
    "secret_key": "",
    "cost_threshold": 0.01
  },
  "volcengine": {
    "enabled": true,
    "default_region": "cn-beijing",
    "access_key_id": "",
    "secret_access_key": "",
    "cost_threshold": 0.01
  },
  "multi_cloud": {
    "enabled": true,
    "providers": ["aws", "aliyun", "tencent", "volcengine"],
    "currency_conversion": {
      "enabled": false,
      "base_currency": "USD",
      "exchange_rates": {
        "CNY": 7.2
      }
    }
  }
}
```

---

## 📊 使用场景和分析方法

### 🎯 单云平台分析

```bash
# AWS专用分析
python3 cloud_cost_analyzer.py quick
python3 cloud_cost_analyzer.py custom --start 2024-01-01 --end 2024-12-31

# 只分析特定云平台（通过配置文件控制）
# 在config.json中设置其他云平台的enabled为false
```

### 🌐 多云对比分析

```bash
# 全平台费用对比
python3 cloud_cost_analyzer.py multi-cloud

# 生成详细报告
python3 cloud_cost_analyzer.py multi-cloud --format all --output ./reports

# 只生成文本报告
python3 cloud_cost_analyzer.py multi-cloud --format txt
```

### 🔍 连接状态检查

```bash
# 检查所有云平台连接状态
python3 cloud_cost_analyzer.py config

# 输出示例：
# ✅ AWS连接: 成功 - 账户ID: 123456789012
# ✅ 阿里云连接: 成功 - 账户余额: 1000.00 元
# ✅ 腾讯云连接: 成功 - 账户余额: 500.00 元
# ✅ 火山云连接: 成功 - 可用余额: 200.00 元
```

### 📈 定时分析

```bash
# 设置每日自动多云分析
crontab -e

# 添加定时任务（每天早上8点）
0 8 * * * cd /path/to/cloud-cost-analyzer && python3 cloud_cost_analyzer.py multi-cloud >> cron.log 2>&1
```

---

## ⚠️ 安全注意事项

### 🔒 密钥安全

1. **使用最小权限原则**
   - 只授予必要的费用查询权限
   - 避免授予写入或管理权限

2. **定期轮换密钥**
   - 建议每3-6个月更换一次API密钥
   - 及时删除不用的密钥

3. **环境变量优先**
   - 优先使用环境变量存储敏感信息
   - 避免在代码中硬编码密钥

4. **配置文件保护**
   ```bash
   # 设置配置文件权限
   chmod 600 config.json
   
   # 添加到.gitignore
   echo "config.json" >> .gitignore
   ```

### 🛡️ 网络安全

1. **API调用频率限制**
   - 各云平台都有API调用频率限制
   - 程序已内置重试机制和频率控制

2. **区域选择**
   - 选择距离最近的区域以提高访问速度
   - 确保选择的区域支持计费API

---

## 🚨 故障排除

### 常见错误及解决方案

#### AWS相关
```
❌ 错误：AccessDenied
✅ 解决：检查IAM用户是否有ce:GetCostAndUsage权限

❌ 错误：InvalidUserID.NotFound  
✅ 解决：检查Access Key是否正确，是否已激活
```

#### 阿里云相关
```
❌ 错误：SignatureDoesNotMatch
✅ 解决：检查AccessKey Secret是否正确

❌ 错误：Forbidden.RAM
✅ 解决：检查RAM用户是否有BSS权限
```

#### 腾讯云相关
```
❌ 错误：AuthFailure.SignatureFailure
✅ 解决：检查SecretId和SecretKey是否正确

❌ 错误：UnauthorizedOperation
✅ 解决：检查用户是否有计费查询权限
```

#### 火山云相关
```
❌ 错误：InvalidAccessKeyId
✅ 解决：检查Access Key ID是否正确

❌ 错误：SignatureDoesNotMatch
✅ 解决：检查Secret Access Key是否正确
```

### 调试命令

```bash
# 详细日志输出
python3 cloud_cost_analyzer.py config 2>&1 | tee debug.log

# 测试单个平台连接
python3 -c "
from src.cloud_cost_analyzer.core.aliyun_client import AliyunClient
client = AliyunClient()
print(client.test_connection())
"
```

---

## 📞 技术支持

如果在配置过程中遇到问题：

1. **查看日志文件** - 检查详细错误信息
2. **验证权限配置** - 确保API密钥有正确的权限
3. **网络连接测试** - 确保能访问各云平台API
4. **提交Issue** - 在GitHub仓库提交问题报告

---

## 🎉 配置完成

完成上述配置后，您就可以使用Cloud Cost Analyzer进行全面的多云费用分析了！

```bash
# 开始您的多云费用分析之旅
python3 cloud_cost_analyzer.py multi-cloud
```
