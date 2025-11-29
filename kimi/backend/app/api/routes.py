from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.schemas.schemas import (
    DataSourceCreate, DataSourceUpdate, DataSourceResponse,
    MigrationTaskCreate, MigrationTaskUpdate, MigrationTaskResponse,
    Response
)
from app.services.datasource_service import DataSourceService
from app.services.migration_service import MigrationTaskService

# 创建主路由
api_router = APIRouter()

# 数据源相关路由
@api_router.post("/datasources", response_model=Response)
async def create_datasource(
    datasource: DataSourceCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建数据源"""
    try:
        # 检查数据源名称是否已存在
        existing = await DataSourceService.get_datasources(db)
        if any(ds.name == datasource.name for ds in existing):
            return Response(
                success=False,
                message=f"数据源名称 '{datasource.name}' 已存在"
            )
        
        # 测试连接
        from app.services.database_service import DatabaseConnection
        connection = DatabaseConnection(
            db_type=datasource.db_type,
            host=datasource.host,
            port=datasource.port,
            database=datasource.database,
            username=datasource.username,
            password=datasource.password
        )
        
        if not await connection.test_connection():
            return Response(
                success=False,
                message="数据库连接测试失败，请检查连接参数"
            )
        
        # 创建数据源
        created_datasource = await DataSourceService.create_datasource(db, datasource)
        return Response(
            success=True,
            message="数据源创建成功",
            data=DataSourceResponse.from_orm(created_datasource)
        )
    except Exception as e:
        return Response(
            success=False,
            message=f"创建数据源失败: {str(e)}"
        )


@api_router.get("/datasources", response_model=Response)
async def get_datasources(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取数据源列表"""
    try:
        datasources = await DataSourceService.get_datasources(db, skip, limit)
        return Response(
            success=True,
            message="获取数据源列表成功",
            data=[DataSourceResponse.from_orm(ds) for ds in datasources]
        )
    except Exception as e:
        return Response(
            success=False,
            message=f"获取数据源列表失败: {str(e)}"
        )


@api_router.get("/datasources/{datasource_id}", response_model=Response)
async def get_datasource(
    datasource_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个数据源"""
    try:
        datasource = await DataSourceService.get_datasource(db, datasource_id)
        if not datasource:
            return Response(
                success=False,
                message=f"数据源ID {datasource_id} 不存在"
            )
        
        return Response(
            success=True,
            message="获取数据源成功",
            data=DataSourceResponse.from_orm(datasource)
        )
    except Exception as e:
        return Response(
            success=False,
            message=f"获取数据源失败: {str(e)}"
        )


@api_router.put("/datasources/{datasource_id}", response_model=Response)
async def update_datasource(
    datasource_id: int,
    datasource_update: DataSourceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新数据源"""
    try:
        updated_datasource = await DataSourceService.update_datasource(db, datasource_id, datasource_update)
        if not updated_datasource:
            return Response(
                success=False,
                message=f"数据源ID {datasource_id} 不存在"
            )
        
        return Response(
            success=True,
            message="数据源更新成功",
            data=DataSourceResponse.from_orm(updated_datasource)
        )
    except Exception as e:
        return Response(
            success=False,
            message=f"更新数据源失败: {str(e)}"
        )


@api_router.delete("/datasources/{datasource_id}", response_model=Response)
async def delete_datasource(
    datasource_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除数据源"""
    try:
        success = await DataSourceService.delete_datasource(db, datasource_id)
        if not success:
            return Response(
                success=False,
                message=f"数据源ID {datasource_id} 不存在"
            )
        
        return Response(
            success=True,
            message="数据源删除成功"
        )
    except Exception as e:
        return Response(
            success=False,
            message=f"删除数据源失败: {str(e)}"
        )


@api_router.post("/datasources/{datasource_id}/test", response_model=Response)
async def test_datasource_connection(
    datasource_id: int,
    db: AsyncSession = Depends(get_db)
):
    """测试数据源连接"""
    try:
        success = await DataSourceService.test_datasource_connection(db, datasource_id)
        if success:
            return Response(
                success=True,
                message="数据源连接测试成功"
            )
        else:
            return Response(
                success=False,
                message="数据源连接测试失败"
            )
    except Exception as e:
        return Response(
            success=False,
            message=f"测试数据源连接失败: {str(e)}"
        )


@api_router.get("/datasources/{datasource_id}/tables", response_model=Response)
async def get_datasource_tables(
    datasource_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取数据源的表列表"""
    try:
        tables = await DataSourceService.get_datasource_tables(db, datasource_id)
        return Response(
            success=True,
            message="获取表列表成功",
            data=tables
        )
    except Exception as e:
        return Response(
            success=False,
            message=f"获取表列表失败: {str(e)}"
        )


@api_router.get("/datasources/{datasource_id}/tables/{table_name}/schema", response_model=Response)
async def get_table_schema(
    datasource_id: int,
    table_name: str,
    db: AsyncSession = Depends(get_db)
):
    """获取表结构"""
    try:
        schema = await DataSourceService.get_table_schema(db, datasource_id, table_name)
        return Response(
            success=True,
            message="获取表结构成功",
            data=schema
        )
    except Exception as e:
        return Response(
            success=False,
            message=f"获取表结构失败: {str(e)}"
        )


# 迁移任务相关路由
@api_router.post("/migration-tasks", response_model=Response)
async def create_migration_task(
    task: MigrationTaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建迁移任务"""
    try:
        # 检查源和目标数据源是否存在
        source_ds = await DataSourceService.get_datasource(db, task.source_id)
        target_ds = await DataSourceService.get_datasource(db, task.target_id)
        
        if not source_ds:
            return Response(
                success=False,
                message=f"源数据源ID {task.source_id} 不存在"
            )
        
        if not target_ds:
            return Response(
                success=False,
                message=f"目标数据源ID {task.target_id} 不存在"
            )
        
        created_task = await MigrationTaskService.create_task(db, task)
        return Response(
            success=True,
            message="迁移任务创建成功",
            data=MigrationTaskResponse.from_orm(created_task)
        )
    except Exception as e:
        return Response(
            success=False,
            message=f"创建迁移任务失败: {str(e)}"
        )


@api_router.get("/migration-tasks", response_model=Response)
async def get_migration_tasks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取迁移任务列表"""
    try:
        tasks = await MigrationTaskService.get_tasks(db, skip, limit)
        return Response(
            success=True,
            message="获取迁移任务列表成功",
            data=[MigrationTaskResponse.from_orm(task) for task in tasks]
        )
    except Exception as e:
        return Response(
            success=False,
            message=f"获取迁移任务列表失败: {str(e)}"
        )


@api_router.get("/migration-tasks/{task_id}", response_model=Response)
async def get_migration_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个迁移任务"""
    try:
        task = await MigrationTaskService.get_task(db, task_id)
        if not task:
            return Response(
                success=False,
                message=f"迁移任务ID {task_id} 不存在"
            )
        
        return Response(
            success=True,
            message="获取迁移任务成功",
            data=MigrationTaskResponse.from_orm(task)
        )
    except Exception as e:
        return Response(
            success=False,
            message=f"获取迁移任务失败: {str(e)}"
        )


@api_router.put("/migration-tasks/{task_id}", response_model=Response)
async def update_migration_task(
    task_id: int,
    task_update: MigrationTaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新迁移任务"""
    try:
        updated_task = await MigrationTaskService.update_task(db, task_id, task_update)
        if not updated_task:
            return Response(
                success=False,
                message=f"迁移任务ID {task_id} 不存在"
            )
        
        return Response(
            success=True,
            message="迁移任务更新成功",
            data=MigrationTaskResponse.from_orm(updated_task)
        )
    except Exception as e:
        return Response(
            success=False,
            message=f"更新迁移任务失败: {str(e)}"
        )


@api_router.delete("/migration-tasks/{task_id}", response_model=Response)
async def delete_migration_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除迁移任务"""
    try:
        success = await MigrationTaskService.delete_task(db, task_id)
        if not success:
            return Response(
                success=False,
                message=f"迁移任务ID {task_id} 不存在"
            )
        
        return Response(
            success=True,
            message="迁移任务删除成功"
        )
    except Exception as e:
        return Response(
            success=False,
            message=f"删除迁移任务失败: {str(e)}"
        )


@api_router.post("/migration-tasks/{task_id}/start", response_model=Response)
async def start_migration_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """启动迁移任务"""
    try:
        success = await MigrationTaskService.start_task(db, task_id)
        if success:
            return Response(
                success=True,
                message="迁移任务启动成功"
            )
        else:
            return Response(
                success=False,
                message="迁移任务启动失败，任务可能不存在或状态不正确"
            )
    except Exception as e:
        return Response(
            success=False,
            message=f"启动迁移任务失败: {str(e)}"
        )


@api_router.post("/migration-tasks/{task_id}/cancel", response_model=Response)
async def cancel_migration_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """取消迁移任务"""
    try:
        success = await MigrationTaskService.cancel_task(db, task_id)
        if success:
            return Response(
                success=True,
                message="迁移任务取消成功"
            )
        else:
            return Response(
                success=False,
                message="迁移任务取消失败，任务可能不存在或状态不正确"
            )
    except Exception as e:
        return Response(
            success=False,
            message=f"取消迁移任务失败: {str(e)}"
        )


@api_router.get("/migration-tasks/{task_id}/progress", response_model=Response)
async def get_task_progress(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取任务进度"""
    try:
        progress = await MigrationTaskService.get_task_progress(db, task_id)
        if not progress:
            return Response(
                success=False,
                message=f"迁移任务ID {task_id} 不存在"
            )
        
        return Response(
            success=True,
            message="获取任务进度成功",
            data=progress
        )
    except Exception as e:
        return Response(
            success=False,
            message=f"获取任务进度失败: {str(e)}"
        )