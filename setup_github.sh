#!/bin/bash

echo "🚀 设置 GitHub 仓库"
echo "=================="

# 检查是否已配置 Git 用户信息
if [ -z "$(git config --global user.name)" ]; then
    echo "⚠️  需要配置 Git 用户信息"
    echo "请运行以下命令配置你的 GitHub 信息："
    echo ""
    echo "git config --global user.name \"你的GitHub用户名\""
    echo "git config --global user.email \"你的邮箱地址\""
    echo ""
    echo "例如："
    echo "git config --global user.name \"john_doe\""
    echo "git config --global user.email \"john@example.com\""
    echo ""
    read -p "按回车键继续..."
fi

# 获取仓库名称
REPO_NAME="aws-cost-analyzer"
echo "📁 仓库名称: $REPO_NAME"

# 检查是否已存在远程仓库
if git remote -v | grep -q origin; then
    echo "✅ 远程仓库已配置"
    git remote -v
else
    echo "🔗 添加远程仓库..."
    echo "请在 GitHub 上创建一个新仓库: https://github.com/new"
    echo "仓库名称建议: $REPO_NAME"
    echo "描述: AWS Cost Analyzer - 功能强大的AWS云服务费用分析工具"
    echo ""
    read -p "创建仓库后，请输入你的 GitHub 用户名: " GITHUB_USERNAME
    
    if [ -n "$GITHUB_USERNAME" ]; then
        git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
        echo "✅ 远程仓库已添加: https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    else
        echo "❌ 未输入用户名，跳过远程仓库配置"
        exit 1
    fi
fi

# 推送到 GitHub
echo ""
echo "📤 推送到 GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 成功推送到 GitHub!"
    echo "仓库地址: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo "📋 后续步骤:"
    echo "1. 访问仓库页面查看代码"
    echo "2. 可以添加 Issues 和 Pull Requests"
    echo "3. 可以设置 GitHub Pages 展示项目"
    echo "4. 可以添加 GitHub Actions 进行 CI/CD"
else
    echo "❌ 推送失败，请检查网络连接和权限"
    echo "可能需要配置 GitHub 认证，建议使用 GitHub CLI 或 SSH 密钥"
fi
