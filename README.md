# AWS Cost Analyzer

一个功能强大的AWS云服务费用分析工具，支持命令行界面，可以分析AWS费用趋势、服务分布、区域分析等。

## 🚀 功能特性

- **快速分析** - 分析过去3个月的AWS费用
- **自定义时间范围** - 支持指定任意时间范围
- **多维度分析** - 按服务、区域、时间等维度分析费用
- **美观图表** - 生成专业的PNG图表和HTML仪表板
- **命令行界面** - 支持参数化执行，无需交互
- **自动凭证检测** - 智能检测AWS凭证配置
- **多格式输出** - 支持TXT、HTML、PNG等多种输出格式

## 📦 安装

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/aws-cost-analyzer.git
cd aws-cost-analyzer
```

### 2. 创建虚拟环境
```bash
python3 -m venv aws_cost_env
source aws_cost_env/bin/activate  # Linux/Mac
# 或
aws_cost_env\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 全局安装（可选）
```bash
sudo cp aws_cost_analyzer.py /usr/local/bin/aws_cost_analyzer
```

## 🔧 使用方法

### 基本用法
```bash
aws_cost_analyzer [命令] [选项]
```

### 可用命令
- `quick` - 快速分析过去3个月的费用
- `custom` - 自定义时间范围分析
- `detailed` - 生成详细报告和图表
- `service` - 按服务分析费用
- `region` - 按区域分析费用
- `trend` - 费用趋势分析
- `optimize` - 费用优化建议
- `config` - 配置检查
- `help` - 显示帮助信息

### 使用示例

```bash
# 查看使用指南
aws_cost_analyzer

# 快速分析
aws_cost_analyzer quick

# 自定义时间范围分析
aws_cost_analyzer custom --start 2024-01-01 --end 2024-12-31

# 生成详细报告
aws_cost_analyzer detailed --output ./reports

# 按服务分析并生成PNG图表
aws_cost_analyzer service --format png

# 配置检查
aws_cost_analyzer config
```

### 选项说明

#### 时间范围选项（用于 custom 命令）
- `--start DATE` - 开始日期 (YYYY-MM-DD)
- `--end DATE` - 结束日期 (YYYY-MM-DD)

#### 输出选项
- `--output DIR` - 指定输出目录 (默认: 当前目录)
- `--format FMT` - 输出格式: txt, html, png, all (默认: all)

#### AWS配置选项
- `--profile NAME` - 使用指定的AWS配置文件
- `--no-auto-setup` - 跳过自动AWS凭证设置

## ⚙️ 配置

### AWS凭证配置

程序会自动检测以下AWS凭证配置：

1. 环境变量 (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS配置文件 (`~/.aws/credentials`)
3. IAM角色（如果在EC2上运行）

如果未检测到凭证，程序会提示输入：
- AWS Access Key ID
- AWS Secret Access Key
- AWS Region（默认: us-east-1）

### 权限要求

需要以下AWS权限：
- `ce:GetCostAndUsage` - 获取费用数据
- `ce:GetDimensionValues` - 获取维度值
- `ce:GetUsageReport` - 获取使用报告

## 📊 输出格式

### 文本报告 (TXT)
- 费用摘要
- 按服务分析
- 按区域分析
- 费用趋势

### HTML仪表板
- 交互式图表
- 响应式设计
- 美观的界面

### PNG图表
- 服务费用分布图
- 区域费用分布图
- 费用趋势图
- 综合仪表板

## 🛠️ 技术栈

- **Python 3.7+**
- **boto3** - AWS SDK
- **pandas** - 数据处理
- **matplotlib** - 图表生成
- **seaborn** - 统计图表
- **plotly** - 交互式图表
- **argparse** - 命令行参数解析

## 📁 项目结构

```
aws-cost-analyzer/
├── aws_cost_analyzer.py          # 主程序文件
├── create_beautiful_charts.py    # 美观图表生成器
├── create_beautiful_dashboard.py # 美观HTML仪表板
├── requirements.txt              # 依赖包列表
├── .gitignore                   # Git忽略文件
└── README.md                    # 项目说明
```

## ⚠️ 注意事项

- 首次使用需要配置AWS凭证
- 需要Cost Explorer API访问权限
- 费用数据可能有1-2天延迟
- 建议在虚拟环境中运行

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 支持

如有问题，请提交Issue或联系开发者。
