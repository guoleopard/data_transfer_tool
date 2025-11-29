@echo off
REM 数据迁移工具部署脚本 (Windows)

echo 🚀 开始部署数据迁移工具...
echo ==========================================

REM 检查Python版本
echo 📋 检查Python版本...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python 未安装
    exit /b 1
)

REM 检查pip
echo 📋 检查pip...
python -m pip --version
if %errorlevel% neq 0 (
    echo ❌ pip 未安装
    exit /b 1
)

REM 创建虚拟环境
echo 🔧 创建虚拟环境...
if not exist "venv" (
    python -m venv venv
    echo ✅ 虚拟环境创建成功
) else (
    echo ℹ️  虚拟环境已存在
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo ⬆️  升级pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 📦 安装依赖...
pip install -r requirements.txt

REM 创建环境变量文件
echo ⚙️  创建环境变量文件...
if not exist ".env" (
    copy .env.example .env
    echo ✅ 环境变量文件创建成功
) else (
    echo ℹ️  环境变量文件已存在
)

REM 初始化数据库
echo 🗄️  初始化数据库...
python init_db.py

echo.
echo 🎉 部署完成！
echo ==========================================
echo 📖 使用方法:
echo 1. 激活虚拟环境: venv\Scripts\activate
echo 2. 启动服务: python main.py
echo 3. 访问API文档: http://localhost:8000/docs
echo.
echo ⚠️  请编辑 .env 文件配置您的数据库连接信息
echo.
pause