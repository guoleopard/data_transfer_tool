from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase):
    pass


# 创建异步引擎
engine_options = {
    "echo": settings.DEBUG,
}

# SQLite不支持连接池参数，只在非SQLite数据库中使用
if "sqlite" not in settings.DATABASE_URL.lower():
    engine_options.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_pre_ping": getattr(settings, 'DB_POOL_PRE_PING', True)
    })
else:
    # SQLite使用基础配置
    engine_options["pool_pre_ping"] = getattr(settings, 'DB_POOL_PRE_PING', True)

engine = create_async_engine(
    settings.DATABASE_URL,
    **engine_options
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)