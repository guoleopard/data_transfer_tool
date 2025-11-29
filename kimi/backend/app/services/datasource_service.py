from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
import logging

from app.models.models import DataSource
from app.schemas.schemas import DataSourceCreate, DataSourceUpdate
from app.services.database_service import DatabaseConnection

logger = logging.getLogger(__name__)


class DataSourceService:
    """数据源管理服务"""
    
    @staticmethod
    async def create_datasource(db: AsyncSession, datasource: DataSourceCreate) -> DataSource:
        """创建数据源"""
        db_datasource = DataSource(**datasource.dict())
        db.add(db_datasource)
        await db.commit()
        await db.refresh(db_datasource)
        return db_datasource
    
    @staticmethod
    async def get_datasource(db: AsyncSession, datasource_id: int) -> Optional[DataSource]:
        """获取单个数据源"""
        result = await db.execute(select(DataSource).where(DataSource.id == datasource_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_datasources(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[DataSource]:
        """获取数据源列表"""
        result = await db.execute(select(DataSource).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def update_datasource(db: AsyncSession, datasource_id: int, datasource_update: DataSourceUpdate) -> Optional[DataSource]:
        """更新数据源"""
        result = await db.execute(select(DataSource).where(DataSource.id == datasource_id))
        db_datasource = result.scalar_one_or_none()
        
        if not db_datasource:
            return None
        
        update_data = datasource_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_datasource, field, value)
        
        await db.commit()
        await db.refresh(db_datasource)
        return db_datasource
    
    @staticmethod
    async def delete_datasource(db: AsyncSession, datasource_id: int) -> bool:
        """删除数据源"""
        result = await db.execute(delete(DataSource).where(DataSource.id == datasource_id))
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def test_datasource_connection(db: AsyncSession, datasource_id: int) -> bool:
        """测试数据源连接"""
        datasource = await DataSourceService.get_datasource(db, datasource_id)
        if not datasource:
            return False
        
        try:
            connection = DatabaseConnection(
                db_type=datasource.db_type,
                host=datasource.host,
                port=datasource.port,
                database=datasource.database,
                username=datasource.username,
                password=datasource.password
            )
            return await connection.test_connection()
        except Exception as e:
            logger.error(f"数据源连接测试失败: {str(e)}")
            return False
    
    @staticmethod
    async def get_datasource_tables(db: AsyncSession, datasource_id: int) -> List[dict]:
        """获取数据源的所有表"""
        datasource = await DataSourceService.get_datasource(db, datasource_id)
        if not datasource:
            return []
        
        try:
            connection = DatabaseConnection(
                db_type=datasource.db_type,
                host=datasource.host,
                port=datasource.port,
                database=datasource.database,
                username=datasource.username,
                password=datasource.password
            )
            return await connection.get_tables()
        except Exception as e:
            logger.error(f"获取数据源表列表失败: {str(e)}")
            return []
    
    @staticmethod
    async def get_table_schema(db: AsyncSession, datasource_id: int, table_name: str) -> List[dict]:
        """获取表结构"""
        datasource = await DataSourceService.get_datasource(db, datasource_id)
        if not datasource:
            return []
        
        try:
            connection = DatabaseConnection(
                db_type=datasource.db_type,
                host=datasource.host,
                port=datasource.port,
                database=datasource.database,
                username=datasource.username,
                password=datasource.password
            )
            return await connection.get_table_schema(table_name)
        except Exception as e:
            logger.error(f"获取表结构失败: {str(e)}")
            return []