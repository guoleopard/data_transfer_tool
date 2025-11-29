# 虚拟环境设置脚本

# 创建虚拟环境
echo "Creating virtual environment..."
python -m venv venv

# 激活虚拟环境
echo "Activating virtual environment..."
call venv\Scripts\activate.bat

# 升级pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete! To activate the virtual environment, run: venv\Scripts\activate"