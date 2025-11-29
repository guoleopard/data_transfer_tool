#!/usr/bin/env python
"""
数据迁移工具 - 数据库初始化脚本
"""
import asyncio
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def init_database():
    """初始化数据库"""
    try:
        logger.info("开始初始化数据库...")
        
        # 导入数据库初始化函数
        from app.core.database import init_db
        
        # 执行初始化
        await init_db()
        
        logger.info("✅ 数据库初始化成功!")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        return False

async def create_sample_data():
    """创建示例数据"""
    try:
        logger.info("开始创建示例数据...")
        
        from app.core.database import get_db
        from app.models import DataSource, DatabaseType
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy import select
        
        # 获取数据库会话
        async for db in get_db():
            # 检查是否已有数据
            result = await db.execute(select(DataSource))
            existing_sources = result.scalars().first()
            
            if not existing_sources:
                # 创建示例数据源
                sample_source = DataSource(
                    name="示例MySQL数据库",
                    db_type=DatabaseType.MYSQL,
                    host="localhost",
                    port=3306,
                    database="test_db",
                    username="root",
                    password="password",
                    description="这是一个示例MySQL数据源"
                )
                
                db.add(sample_source)
                await db.commit()
                
                logger.info("✅ 示例数据源创建成功!")
            else:
                logger.info("ℹ️  数据库中已存在数据，跳过示例数据创建")
            
            break
            
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建示例数据失败: {e}")
        return False

async def main():
    """主函数"""
    print("🚀 数据迁移工具 - 数据库初始化")
    print("=" * 50)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 初始化数据库
    success = await init_database()
    
    if success:
        # 创建示例数据
        await create_sample_data()
        
        print("\n✅ 所有初始化操作完成!")
        print("\n📖 下一步:")
        print("1. 启动服务: python main.py")
        print("2. 访问API文档: http://localhost:8000/docs")
    else:
        print("\n❌ 初始化失败，请检查配置和日志")

if __name__ == "__main__":
    asyncio.run(main())