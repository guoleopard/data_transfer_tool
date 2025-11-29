from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.models import DatabaseType, TaskStatus


# 数据源相关Schema
class DataSourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    db_type: DatabaseType
    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(..., ge=1, le=65535)
    database: str = Field(..., min_length=1, max_length=100)
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    db_type: Optional[DatabaseType] = None
    host: Optional[str] = Field(None, min_length=1, max_length=255)
    port: Optional[int] = Field(None, ge=1, le=65535)
    database: Optional[str] = Field(None, min_length=1, max_length=100)
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None


class DataSourceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    db_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# 迁移任务相关Schema
class MigrationTaskBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    source_id: int
    target_id: int
    source_table: str = Field(..., min_length=1, max_length=100)
    target_table: str = Field(..., min_length=1, max_length=100)
    mapping_config: Optional[str] = None  # JSON字符串
    filter_condition: Optional[str] = None


class MigrationTaskCreate(MigrationTaskBase):
    pass


class MigrationTaskUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    source_id: Optional[int] = None
    target_id: Optional[int] = None
    source_table: Optional[str] = Field(None, min_length=1, max_length=100)
    target_table: Optional[str] = Field(None, min_length=1, max_length=100)
    mapping_config: Optional[str] = None
    filter_condition: Optional[str] = None


class MigrationTaskResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    source_id: int
    target_id: int
    source_table: str
    target_table: str
    mapping_config: Optional[str]
    filter_condition: Optional[str]
    status: TaskStatus
    progress: int
    total_rows: int
    processed_rows: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# 通用响应Schema
class Response(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    detail: Optional[str] = None