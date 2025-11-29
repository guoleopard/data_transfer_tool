from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "数据迁移工具"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./data_transfer.db"
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # 数据库连接池配置
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    
    # 迁移任务配置
    MAX_CONCURRENT_TASKS: int = 3
    TASK_TIMEOUT: int = 3600  # 秒
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()