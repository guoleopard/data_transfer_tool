#!/bin/bash

# 数据迁移工具部署脚本

set -e

echo "🚀 开始部署数据迁移工具..."
echo "=========================================="

# 检查Python版本
echo "📋 检查Python版本..."
python3 --version || { echo "❌ Python3 未安装"; exit 1; }

# 检查pip
echo "📋 检查pip..."
python3 -m pip --version || { echo "❌ pip 未安装"; exit 1; }

# 创建虚拟环境
echo "🔧 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "ℹ️  虚拟环境已存在"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "⬆️  升级pip..."
python -m pip install --upgrade pip

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt

# 创建环境变量文件
echo "⚙️  创建环境变量文件..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ 环境变量文件创建成功"
else
    echo "ℹ️  环境变量文件已存在"
fi

# 初始化数据库
echo "🗄️  初始化数据库..."
python init_db.py

# 设置文件权限
echo "🔒 设置文件权限..."
chmod +x setup_env.sh
chmod +x init_db.py

echo ""
echo "🎉 部署完成！"
echo "=========================================="
echo "📖 使用方法:"
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 启动服务: python main.py"
echo "3. 访问API文档: http://localhost:8000/docs"
echo ""
echo "⚠️  请编辑 .env 文件配置您的数据库连接信息"