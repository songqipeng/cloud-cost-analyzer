"""
多云费用分析器安装配置
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="multi-cloud-analyzer",
    version="2.0.0",
    author="Multi-Cloud Analyzer Team", 
    author_email="",
    description="一个功能强大的多云费用分析工具，支持AWS、阿里云、腾讯云、火山云",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/songqipeng/multi-cloud-analyzer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: System :: Systems Administration",
        "Topic :: Office/Business :: Financial",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "multi-cloud-analyzer=aws_cost_analyzer:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
