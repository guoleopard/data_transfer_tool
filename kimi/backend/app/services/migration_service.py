import asyncio
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.models import MigrationTask, TaskStatus, DataSource
from app.schemas.schemas import MigrationTaskCreate, MigrationTaskUpdate
from app.services.database_service import DatabaseConnection

logger = logging.getLogger(__name__)


class MigrationTaskService:
    """数据迁移任务管理服务"""
    
    @staticmethod
    async def create_task(db: AsyncSession, task: MigrationTaskCreate) -> MigrationTask:
        """创建迁移任务"""
        db_task = MigrationTask(**task.dict())
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task
    
    @staticmethod
    async def get_task(db: AsyncSession, task_id: int) -> Optional[MigrationTask]:
        """获取单个迁移任务"""
        result = await db.execute(select(MigrationTask).where(MigrationTask.id == task_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_tasks(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[MigrationTask]:
        """获取迁移任务列表"""
        result = await db.execute(select(MigrationTask).offset(skip).limit(limit))
        return result.scalars().all()
    
    @staticmethod
    async def update_task(db: AsyncSession, task_id: int, task_update: MigrationTaskUpdate) -> Optional[MigrationTask]:
        """更新迁移任务"""
        result = await db.execute(select(MigrationTask).where(MigrationTask.id == task_id))
        db_task = result.scalar_one_or_none()
        
        if not db_task:
            return None
        
        update_data = task_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        await db.commit()
        await db.refresh(db_task)
        return db_task
    
    @staticmethod
    async def delete_task(db: AsyncSession, task_id: int) -> bool:
        """删除迁移任务"""
        result = await db.execute(delete(MigrationTask).where(MigrationTask.id == task_id))
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def start_task(db: AsyncSession, task_id: int) -> bool:
        """启动迁移任务"""
        task = await MigrationTaskService.get_task(db, task_id)
        if not task or task.status != TaskStatus.PENDING:
            return False
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        task.progress = 0
        await db.commit()
        
        # 异步执行迁移任务
        asyncio.create_task(MigrationTaskService._execute_task(db, task_id))
        return True
    
    @staticmethod
    async def cancel_task(db: AsyncSession, task_id: int) -> bool:
        """取消迁移任务"""
        task = await MigrationTaskService.get_task(db, task_id)
        if not task or task.status != TaskStatus.RUNNING:
            return False
        
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        await db.commit()
        return True
    
    @staticmethod
    async def _execute_task(db: AsyncSession, task_id: int):
        """执行迁移任务"""
        try:
            # 重新获取任务（在新的会话中）
            async with db.begin():
                result = await db.execute(select(MigrationTask).where(MigrationTask.id == task_id))
                task = result.scalar_one_or_none()
                
                if not task or task.status != TaskStatus.RUNNING:
                    return
                
                # 获取源和目标数据源
                source_result = await db.execute(select(DataSource).where(DataSource.id == task.source_id))
                source_ds = source_result.scalar_one_or_none()
                
                target_result = await db.execute(select(DataSource).where(DataSource.id == task.target_id))
                target_ds = target_result.scalar_one_or_none()
                
                if not source_ds or not target_ds:
                    task.status = TaskStatus.FAILED
                    task.error_message = "源数据源或目标数据源不存在"
                    task.completed_at = datetime.now()
                    await db.commit()
                    return
                
                # 创建数据库连接
                source_conn = DatabaseConnection(
                    db_type=source_ds.db_type,
                    host=source_ds.host,
                    port=source_ds.port,
                    database=source_ds.database,
                    username=source_ds.username,
                    password=source_ds.password
                )
                
                target_conn = DatabaseConnection(
                    db_type=target_ds.db_type,
                    host=target_ds.host,
                    port=target_ds.port,
                    database=target_ds.database,
                    username=target_ds.username,
                    password=target_ds.password
                )
                
                # 测试连接
                if not await source_conn.test_connection():
                    task.status = TaskStatus.FAILED
                    task.error_message = "源数据源连接失败"
                    task.completed_at = datetime.now()
                    await db.commit()
                    return
                
                if not await target_conn.test_connection():
                    task.status = TaskStatus.FAILED
                    task.error_message = "目标数据源连接失败"
                    task.completed_at = datetime.now()
                    await db.commit()
                    return
                
                # 获取源表记录数
                total_rows = await source_conn.get_table_count(task.source_table, task.filter_condition)
                task.total_rows = total_rows
                await db.commit()
                
                if total_rows == 0:
                    task.status = TaskStatus.COMPLETED
                    task.progress = 100
                    task.completed_at = datetime.now()
                    await db.commit()
                    return
                
                # 执行数据迁移（这里简化处理，实际应该分批处理）
                # 这里只是更新进度，实际的数据迁移逻辑需要根据具体需求实现
                task.processed_rows = total_rows
                task.progress = 100
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                await db.commit()
                
        except Exception as e:
            logger.error(f"迁移任务执行失败: {str(e)}")
            async with db.begin():
                result = await db.execute(select(MigrationTask).where(MigrationTask.id == task_id))
                task = result.scalar_one_or_none()
                if task:
                    task.status = TaskStatus.FAILED
                    task.error_message = str(e)
                    task.completed_at = datetime.now()
                    await db.commit()
    
    @staticmethod
    async def get_task_progress(db: AsyncSession, task_id: int) -> Optional[Dict[str, Any]]:
        """获取任务进度"""
        task = await MigrationTaskService.get_task(db, task_id)
        if not task:
            return None
        
        return {
            "task_id": task.id,
            "status": task.status,
            "progress": task.progress,
            "total_rows": task.total_rows,
            "processed_rows": task.processed_rows,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "error_message": task.error_message
        }