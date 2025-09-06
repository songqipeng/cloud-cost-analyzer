# 多阶段Docker构建
FROM python:3.11-slim as builder

# 设置构建参数
ARG DEBIAN_FRONTEND=noninteractive
ARG BUILD_DATE
ARG VCS_REF

# 添加标签
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="cloud-cost-analyzer" \
      org.label-schema.description="Multi-cloud cost analysis tool" \
      org.label-schema.version="2.0.0" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/songqipeng/cloud-cost-analyzer" \
      org.label-schema.schema-version="1.0" \
      maintainer="Cloud Cost Analyzer Team"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 升级pip并安装构建工具
RUN pip install --no-cache-dir --upgrade pip setuptools wheel build

# 复制项目配置文件
COPY pyproject.toml README.md ./

# 安装Python依赖
RUN pip install --no-cache-dir -e .[dev] --no-deps || \
    pip install --no-cache-dir \
    boto3>=1.34.0,\<2.0.0 \
    pandas>=2.2.0,\<3.0.0 \
    matplotlib>=3.8.0,\<4.0.0 \
    seaborn>=0.13.0,\<1.0.0 \
    plotly>=5.17.0,\<6.0.0 \
    python-dateutil>=2.8.2,\<3.0.0 \
    rich>=13.0.0,\<14.0.0 \
    colorama>=0.4.6,\<1.0.0 \
    requests>=2.31.0,\<3.0.0 \
    schedule>=1.2.0,\<2.0.0 \
    alibabacloud-bssopenapi20171214>=2.0.0,\<3.0.0 \
    tencentcloud-sdk-python>=3.0.0,\<4.0.0 \
    volcengine-python-sdk>=1.0.0,\<2.0.0 \
    click>=8.0.0,\<9.0.0 \
    redis>=4.5.0,\<5.0.0 \
    aiohttp>=3.8.0,\<4.0.0 \
    pydantic>=2.0.0,\<3.0.0

# 复制源代码
COPY src/ ./src/
COPY tests/ ./tests/
COPY cloud_cost_analyzer.py ./

# 构建应用程序
RUN python -m build

# 生产阶段
FROM python:3.11-slim as production

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 创建非root用户
RUN groupadd -r cloudcost && useradd -r -g cloudcost -s /bin/bash cloudcost

# 设置工作目录
WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 从构建阶段复制Python包
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app/src/ ./src/

# 复制主程序
COPY cloud_cost_analyzer.py ./
COPY config.example.json ./config.json

# 创建必要的目录
RUN mkdir -p /app/.cache /app/reports /app/logs \
    && chown -R cloudcost:cloudcost /app

# 切换到非root用户
USER cloudcost

# 设置Python路径
ENV PYTHONPATH=/app/src

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.path.insert(0, 'src'); from cloud_cost_analyzer.utils.config import Config; print('OK')" || exit 1

# 暴露端口（如果将来添加Web界面）
EXPOSE 8080

# 设置默认命令
ENTRYPOINT ["python", "cloud_cost_analyzer.py"]
CMD ["--help"]

# 开发阶段（用于开发环境）
FROM builder as development

# 安装开发依赖
RUN pip install --no-cache-dir \
    pytest>=7.0.0 \
    pytest-cov>=4.0.0 \
    pytest-mock>=3.10.0 \
    pytest-asyncio>=0.21.0 \
    black>=23.0.0 \
    flake8>=6.0.0 \
    mypy>=1.0.0 \
    pre-commit>=3.0.0 \
    bandit>=1.7.0 \
    safety>=2.3.0

# 复制开发配置
COPY .pre-commit-config.yaml Makefile ./

# 设置开发环境变量
ENV FLASK_ENV=development \
    PYTHONPATH=/app/src

# 创建开发用户目录
RUN mkdir -p /home/cloudcost \
    && chown -R cloudcost:cloudcost /home/cloudcost

USER cloudcost

# 开发模式默认命令
CMD ["bash"]