"""
主入口文件
"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from cloud_cost_analyzer.cli.commands import cli


def main():
    """主入口函数"""
    cli()


if __name__ == '__main__':
    main()