# Docker 使用指南

## 🐳 快速开始

### 1. 环境准备

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑环境变量
vim .env
```

### 2. 构建和运行

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 3. 基本命令

```bash
# 检查配置
docker-compose run --rm cloud-cost-analyzer config

# AWS快速分析
docker-compose run --rm cloud-cost-analyzer quick

# 多云分析
docker-compose run --rm cloud-cost-analyzer multi-cloud

# 自定义时间范围分析
docker-compose run --rm cloud-cost-analyzer custom --start 2024-01-01 --end 2024-12-31
```

## 📋 服务说明

### 主要服务

| 服务名 | 描述 | 端口 |
|--------|------|------|
| `cloud-cost-analyzer` | 主应用服务 | - |
| `redis` | 缓存服务 | 6379 |
| `scheduler` | 定时任务服务 | - |

### 开发服务

```bash
# 启动开发环境
docker-compose --profile dev up -d

# 进入开发容器
docker-compose exec dev bash

# 运行测试
docker-compose exec dev make test

# 代码格式化
docker-compose exec dev make format
```

## 🗂️ 目录映射

| 容器路径 | 宿主机路径 | 说明 |
|----------|-----------|------|
| `/app/config.json` | `./config.json` | 配置文件 |
| `/app/reports` | `./reports` | 报告输出 |
| `/app/logs` | `./logs` | 日志文件 |
| `/app/.cache` | 卷挂载 | 缓存数据 |

## ⚙️ 环境变量

### 必需变量

```bash
# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1

# 阿里云
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_secret_key

# 腾讯云
TENCENTCLOUD_SECRET_ID=your_secret_id
TENCENTCLOUD_SECRET_KEY=your_secret_key

# 火山云
VOLCENGINE_ACCESS_KEY_ID=your_access_key
VOLCENGINE_SECRET_ACCESS_KEY=your_secret_key
```

### 可选变量

```bash
# Redis
REDIS_PASSWORD=your_redis_password

# 邮件通知
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
NOTIFICATION_EMAIL=recipient@example.com

# 飞书通知
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
FEISHU_SECRET=your_secret_key

# 应用配置
LOG_LEVEL=INFO
CACHE_TYPE=redis
CACHE_TTL=3600
```

## 🔧 高级配置

### 1. 自定义配置文件

```bash
# 创建自定义配置
cp config.example.json config.json

# 编辑配置
vim config.json

# 重启服务使配置生效
docker-compose restart cloud-cost-analyzer
```

### 2. 定时任务配置

默认每天早上8点运行多云分析，可以通过修改 `docker-compose.yml` 中的 cron 表达式来调整：

```yaml
command: >
  sh -c "
  echo '0 8 * * * cd /app && python cloud_cost_analyzer.py multi-cloud >> /app/logs/cron.log 2>&1' | crontab -
  crond -f
  "
```

### 3. 缓存配置

默认使用 Redis 缓存，可以通过环境变量调整：

```bash
# 使用内存缓存
CACHE_TYPE=memory

# 使用文件缓存
CACHE_TYPE=file

# 调整缓存TTL（秒）
CACHE_TTL=7200
```

## 🚀 生产部署

### 1. 使用 Docker Swarm

```bash
# 初始化 Swarm
docker swarm init

# 部署服务栈
docker stack deploy -c docker-compose.yml cloud-cost-stack

# 查看服务状态
docker stack services cloud-cost-stack

# 扩展服务
docker service scale cloud-cost-stack_cloud-cost-analyzer=3
```

### 2. 使用 Kubernetes

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloud-cost-analyzer
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cloud-cost-analyzer
  template:
    metadata:
      labels:
        app: cloud-cost-analyzer
    spec:
      containers:
      - name: cloud-cost-analyzer
        image: cloud-cost-analyzer:latest
        env:
        - name: AWS_ACCESS_KEY_ID
          valueFrom:
            secretKeyRef:
              name: cloud-secrets
              key: aws-access-key-id
        # ... 其他环境变量
        volumeMounts:
        - name: config-volume
          mountPath: /app/config.json
          subPath: config.json
      volumes:
      - name: config-volume
        configMap:
          name: cloud-cost-config
```

### 3. 监控和日志

```bash
# 查看服务健康状态
docker-compose ps

# 实时日志
docker-compose logs -f --tail=100

# 查看特定服务日志
docker-compose logs -f cloud-cost-analyzer

# 查看资源使用情况
docker stats

# 清理未使用的资源
docker system prune -f
```

## 🔍 故障排除

### 1. 常见问题

**问题**: 容器无法启动
```bash
# 检查日志
docker-compose logs cloud-cost-analyzer

# 检查配置
docker-compose config

# 重建镜像
docker-compose build --no-cache
```

**问题**: 连接云服务失败
```bash
# 检查环境变量
docker-compose exec cloud-cost-analyzer env | grep -E "(AWS|ALIBABA|TENCENT|VOLCENGINE)"

# 测试连接
docker-compose run --rm cloud-cost-analyzer config
```

**问题**: Redis 连接失败
```bash
# 检查 Redis 状态
docker-compose exec redis redis-cli ping

# 查看 Redis 日志
docker-compose logs redis

# 重启 Redis
docker-compose restart redis
```

### 2. 性能调优

```bash
# 限制内存使用
docker-compose run --rm -m 512m cloud-cost-analyzer multi-cloud

# 设置CPU限制
docker-compose run --rm --cpus="1.0" cloud-cost-analyzer multi-cloud

# 查看资源使用
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### 3. 备份和恢复

```bash
# 备份缓存数据
docker run --rm -v cloud-cost-analyzer_cache_data:/data -v $(pwd):/backup alpine tar czf /backup/cache-backup.tar.gz -C /data .

# 恢复缓存数据
docker run --rm -v cloud-cost-analyzer_cache_data:/data -v $(pwd):/backup alpine sh -c "cd /data && tar xzf /backup/cache-backup.tar.gz"

# 备份配置
cp config.json config-backup-$(date +%Y%m%d).json
```

## 📊 监控指标

### 1. 应用指标

- 分析任务执行时间
- API 调用成功率
- 缓存命中率
- 错误率

### 2. 系统指标

- CPU 使用率
- 内存使用率
- 磁盘使用率
- 网络流量

### 3. 自定义指标

可以通过修改应用代码添加 Prometheus 指标：

```python
from prometheus_client import Counter, Histogram, Gauge

# 计数器
api_calls_total = Counter('api_calls_total', 'Total API calls', ['provider', 'status'])

# 直方图
analysis_duration = Histogram('analysis_duration_seconds', 'Analysis duration')

# 仪表盘
cache_size = Gauge('cache_size', 'Current cache size')
```

## 🛡️ 安全建议

### 1. 密钥管理

- 使用 Docker Secrets 或 Kubernetes Secrets 管理敏感信息
- 定期轮换 API 密钥
- 避免在 Dockerfile 中硬编码密钥

### 2. 网络安全

- 使用自定义网络隔离服务
- 只暴露必要的端口
- 启用 TLS 加密

### 3. 镜像安全

- 定期更新基础镜像
- 扫描镜像漏洞
- 使用最小权限原则

```bash
# 扫描镜像漏洞
docker scan cloud-cost-analyzer:latest

# 检查镜像大小
docker images cloud-cost-analyzer
```