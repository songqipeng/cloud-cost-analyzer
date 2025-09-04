#!/bin/bash

echo "🚀 AWS Cost Analyzer - GitHub 部署助手"
echo "======================================"
echo ""

# 检查Git状态
echo "📋 检查Git状态..."
if [ ! -d ".git" ]; then
    echo "❌ 当前目录不是Git仓库"
    exit 1
fi

echo "✅ Git仓库已存在"
echo ""

# 显示当前提交状态
echo "📊 当前提交状态:"
git log --oneline -5
echo ""

# 获取GitHub用户名
echo "🔑 请输入你的GitHub用户名:"
read -p "GitHub用户名: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ 用户名不能为空"
    exit 1
fi

# 仓库名称
REPO_NAME="aws-cost-analyzer"
REPO_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

echo ""
echo "📁 仓库信息:"
echo "   用户名: $GITHUB_USERNAME"
echo "   仓库名: $REPO_NAME"
echo "   仓库URL: $REPO_URL"
echo ""

# 检查是否已配置远程仓库
if git remote -v | grep -q origin; then
    echo "✅ 远程仓库已配置:"
    git remote -v
    echo ""
    read -p "是否要更新远程仓库URL? (y/n): " UPDATE_REMOTE
    if [ "$UPDATE_REMOTE" = "y" ] || [ "$UPDATE_REMOTE" = "Y" ]; then
        git remote set-url origin "$REPO_URL"
        echo "✅ 远程仓库URL已更新"
    fi
else
    echo "🔗 添加远程仓库..."
    git remote add origin "$REPO_URL"
    echo "✅ 远程仓库已添加"
fi

echo ""
echo "📝 请按照以下步骤在GitHub上创建仓库:"
echo ""
echo "1. 打开浏览器访问: https://github.com/new"
echo "2. 填写仓库信息:"
echo "   - Repository name: $REPO_NAME"
echo "   - Description: AWS Cost Analyzer - 功能强大的AWS云服务费用分析工具"
echo "   - 选择 Public 或 Private"
echo "   - 不要勾选任何初始化选项"
echo "3. 点击 'Create repository'"
echo ""

read -p "创建仓库完成后，按回车键继续..."

echo ""
echo "📤 开始推送到GitHub..."

# 推送到GitHub
if git push -u origin main; then
    echo ""
    echo "🎉 成功推送到GitHub!"
    echo ""
    echo "📋 仓库信息:"
    echo "   仓库地址: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo "   克隆命令: git clone https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo ""
    echo "🔗 有用的链接:"
    echo "   - 仓库页面: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo "   - Issues: https://github.com/$GITHUB_USERNAME/$REPO_NAME/issues"
    echo "   - Settings: https://github.com/$GITHUB_USERNAME/$REPO_NAME/settings"
    echo ""
    echo "✅ 部署完成！你的AWS Cost Analyzer已经成功上传到GitHub了！"
else
    echo ""
    echo "❌ 推送失败！可能的原因:"
    echo "   1. 仓库尚未创建"
    echo "   2. 网络连接问题"
    echo "   3. 认证问题"
    echo ""
    echo "🔧 解决方案:"
    echo "   1. 确保已在GitHub上创建仓库"
    echo "   2. 检查网络连接"
    echo "   3. 可能需要配置GitHub认证"
    echo ""
    echo "💡 提示: 如果使用HTTPS，可能需要输入GitHub用户名和密码"
    echo "   建议使用Personal Access Token替代密码"
fi
