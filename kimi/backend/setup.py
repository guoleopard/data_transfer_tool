#!/usr/bin/env python
import asyncio
import logging
from datetime import datetime
import json

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def setup_database():
    """初始化数据库"""
    try:
        from app.core.database import init_db
        await init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

def main():
    """主函数"""
    print("🚀 数据迁移工具后端服务")
    print("=" * 50)
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("📋 快速开始:")
    print("1. 激活虚拟环境: venv\\Scripts\\activate")
    print("2. 安装依赖: pip install -r requirements.txt")
    print("3. 配置环境: cp .env.example .env")
    print("4. 运行服务: python main.py")
    print()
    print("📖 API文档:")
    print("- Swagger UI: http://localhost:8000/docs")
    print("- ReDoc: http://localhost:8000/redoc")
    print()
    print("🔧 开发工具:")
    print("- 数据库初始化: python init_db.py")
    print("- 运行测试: python -m pytest")
    print()

if __name__ == "__main__":
    main()
    
    # 可选：初始化数据库
    try:
        asyncio.run(setup_database())
    except Exception:
        pass