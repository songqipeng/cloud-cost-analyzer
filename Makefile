.PHONY: help install install-dev test test-coverage lint format type-check security-check clean build docker-build docker-run pre-commit-install run-quick run-multi-cloud docs

# 默认目标
help:
	@echo "Cloud Cost Analyzer - 开发工具命令"
	@echo ""
	@echo "安装和设置:"
	@echo "  install           安装生产依赖"
	@echo "  install-dev       安装开发依赖"
	@echo "  pre-commit-install 安装pre-commit钩子"
	@echo ""
	@echo "测试:"
	@echo "  test              运行测试"
	@echo "  test-coverage     运行测试并生成覆盖率报告"
	@echo "  test-integration  运行集成测试"
	@echo ""
	@echo "代码质量:"
	@echo "  lint              运行所有代码检查"
	@echo "  format            格式化代码"
	@echo "  type-check        类型检查"
	@echo "  security-check    安全检查"
	@echo ""
	@echo "构建和运行:"
	@echo "  clean             清理构建文件"
	@echo "  build             构建项目"
	@echo "  docker-build      构建Docker镜像"
	@echo "  docker-run        运行Docker容器"
	@echo ""
	@echo "应用命令:"
	@echo "  run-quick         快速AWS分析"
	@echo "  run-multi-cloud   多云分析"
	@echo "  run-config        检查配置"
	@echo ""
	@echo "文档:"
	@echo "  docs              生成文档"

# 安装依赖
install:
	pip install -e .

install-dev:
	pip install -e .[dev,jupyter]

pre-commit-install:
	pre-commit install

# 测试
test:
	python -m pytest tests/ -v

test-coverage:
	python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml

test-integration:
	python -m pytest tests/ -v -m integration

test-unit:
	python -m pytest tests/ -v -m unit

# 代码质量检查
lint: type-check security-check
	flake8 src tests
	black --check src tests
	isort --check-only src tests

format:
	black src tests
	isort src tests

type-check:
	mypy src --ignore-missing-imports

security-check:
	bandit -r src/ -f json --skip B101,B601
	safety check

# 清理和构建
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf bandit-report.json
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

# Docker
docker-build:
	docker build -t cloud-cost-analyzer .

docker-run:
	docker run --rm -it \
		-e AWS_ACCESS_KEY_ID \
		-e AWS_SECRET_ACCESS_KEY \
		-e ALIBABA_CLOUD_ACCESS_KEY_ID \
		-e ALIBABA_CLOUD_ACCESS_KEY_SECRET \
		-e TENCENTCLOUD_SECRET_ID \
		-e TENCENTCLOUD_SECRET_KEY \
		-e VOLCENGINE_ACCESS_KEY_ID \
		-e VOLCENGINE_SECRET_ACCESS_KEY \
		cloud-cost-analyzer

# 应用命令
run-quick:
	python cloud_cost_analyzer.py quick

run-multi-cloud:
	python cloud_cost_analyzer.py multi-cloud

run-config:
	python cloud_cost_analyzer.py config

# 开发工具
dev-setup: install-dev pre-commit-install
	@echo "开发环境设置完成!"

check-all: lint test-coverage security-check
	@echo "所有检查完成!"

# 生成依赖文件（用于Docker等）
requirements:
	pip-compile pyproject.toml --output-file requirements.lock

# 更新依赖
update-deps:
	pip install --upgrade pip
	pip-compile --upgrade pyproject.toml --output-file requirements.lock
	pip install -r requirements.lock

# 文档生成（如果需要）
docs:
	@echo "文档生成功能待实现"

# CI/CD相关
ci-test: install-dev
	python -m pytest tests/ -v --cov=src --cov-report=xml --junitxml=pytest.xml

ci-lint: install-dev
	flake8 src tests --format=junit-xml --output-file=flake8.xml
	black --check src tests
	mypy src --ignore-missing-imports --junit-xml mypy.xml