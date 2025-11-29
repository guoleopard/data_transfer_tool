from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os

app = FastAPI(title="数据迁移工具后端服务")

# 配置CORS中间件
origins = [
    "http://localhost:5173",  # 前端开发服务器地址
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置 - 使用SQLite作为示例，实际使用时可配置为MySQL或SQL Server
SQLALCHEMY_DATABASE_URL = "sqlite:///./data_transfer.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 数据库模型定义
class DataSource(Base):
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, unique=True, nullable=False)
    type = Column(String(20), nullable=False)  # "mysql" 或 "sqlserver"
    host = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    database = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MigrationTask(Base):
    __tablename__ = "migration_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, unique=True, nullable=False)
    source_id = Column(Integer, nullable=False)
    target_id = Column(Integer, nullable=False)
    table_names = Column(Text)  # 逗号分隔的表名集合，如"table1,table2,table3"
    migrate_structure = Column(Boolean, default=True)  # 是否进行数据库结构迁移
    migrate_records = Column(Boolean, default=True)  # 是否进行数据库记录迁移
    status = Column(String(20), default="pending")  # "pending", "running", "completed", "failed"
    progress = Column(Integer, default=0)
    create_time = Column(DateTime, default=datetime.utcnow)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    log = Column(Text)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# Pydantic模型定义
class DataSourceCreate(BaseModel):
    name: str
    type: str
    host: str
    port: int
    database: str
    username: str
    password: str

class DataSourceUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    host: str | None = None
    port: int | None = None
    database: str | None = None
    username: str | None = None
    password: str | None = None

class MigrationTaskCreate(BaseModel):
    name: str
    source_id: int
    target_id: int
    table_names: str | None = None
    migrate_structure: bool = True
    migrate_records: bool = True

class MigrationTaskUpdate(BaseModel):
    name: str | None = None
    source_id: int | None = None
    target_id: int | None = None
    table_names: str | None = None
    migrate_structure: bool | None = None
    migrate_records: bool | None = None
    status: str | None = None
    progress: int | None = None
    log: str | None = None

# 依赖函数：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 数据源管理API
@app.post("/api/data_sources/", response_model=dict)
def create_data_source(source: DataSourceCreate, db: Session = Depends(get_db)):
    # 检查数据源类型是否合法
    if source.type not in ["mysql", "sqlserver"]:
        raise HTTPException(status_code=400, detail="不支持的数据库类型，仅支持mysql和sqlserver")
    
    # 检查数据源名称是否已存在
    if db.query(DataSource).filter(DataSource.name == source.name).first():
        raise HTTPException(status_code=400, detail="数据源名称已存在")
    
    db_source = DataSource(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return {"id": db_source.id, "name": db_source.name, "message": "数据源创建成功"}

@app.get("/api/data_sources/", response_model=list[dict])
def get_data_sources(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    sources = db.query(DataSource).offset(skip).limit(limit).all()
    return [{"id": s.id, "name": s.name, "type": s.type, "host": s.host, "port": s.port, "database": s.database, "create_time": s.create_time} for s in sources]

@app.get("/api/data_sources/{source_id}", response_model=dict)
def get_data_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    return {"id": source.id, "name": source.name, "type": source.type, "host": source.host, "port": source.port, "database": source.database, "username": source.username, "create_time": source.create_time}

@app.put("/api/data_sources/{source_id}", response_model=dict)
def update_data_source(source_id: int, source: DataSourceUpdate, db: Session = Depends(get_db)):
    db_source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    # 检查新名称是否已存在（如果更新了名称）
    if source.name and source.name != db_source.name:
        if db.query(DataSource).filter(DataSource.name == source.name).first():
            raise HTTPException(status_code=400, detail="数据源名称已存在")
    
    # 更新字段
    update_data = source.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_source, key, value)
    
    db.commit()
    db.refresh(db_source)
    return {"id": db_source.id, "name": db_source.name, "message": "数据源更新成功"}

@app.delete("/api/data_sources/{source_id}", response_model=dict)
def delete_data_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")
    
    db.delete(source)
    db.commit()
    return {"id": source_id, "message": "数据源删除成功"}

# 数据迁移任务管理API
@app.post("/api/migration_tasks/", response_model=dict)
def create_migration_task(task: MigrationTaskCreate, db: Session = Depends(get_db)):
    # 检查源和目标数据源是否存在
    source = db.query(DataSource).filter(DataSource.id == task.source_id).first()
    target = db.query(DataSource).filter(DataSource.id == task.target_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="源数据源不存在")
    if not target:
        raise HTTPException(status_code=404, detail="目标数据源不存在")
    
    # 检查任务名称是否已存在
    if db.query(MigrationTask).filter(MigrationTask.name == task.name).first():
        raise HTTPException(status_code=400, detail="任务名称已存在")
    
    db_task = MigrationTask(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return {"id": db_task.id, "name": db_task.name, "message": "迁移任务创建成功"}

@app.get("/api/migration_tasks/", response_model=list[dict])
def get_migration_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    tasks = db.query(MigrationTask).offset(skip).limit(limit).all()
    return [{"id": t.id, "name": t.name, "source_id": t.source_id, "target_id": t.target_id, "table_names": t.table_names, "migrate_structure": t.migrate_structure, "migrate_records": t.migrate_records, "status": t.status, "progress": t.progress, "create_time": t.create_time} for t in tasks]

@app.get("/api/migration_tasks/{task_id}", response_model=dict)
def get_migration_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(MigrationTask).filter(MigrationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="迁移任务不存在")
    return {"id": task.id, "name": task.name, "source_id": task.source_id, "target_id": task.target_id, "table_names": task.table_names, "migrate_structure": task.migrate_structure, "migrate_records": task.migrate_records, "status": task.status, "progress": task.progress, "log": task.log, "create_time": task.create_time, "update_time": task.update_time}

@app.put("/api/migration_tasks/{task_id}", response_model=dict)
def update_migration_task(task_id: int, task: MigrationTaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(MigrationTask).filter(MigrationTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="迁移任务不存在")
    
    # 检查新名称是否已存在（如果更新了名称）
    if task.name and task.name != db_task.name:
        if db.query(MigrationTask).filter(MigrationTask.name == task.name).first():
            raise HTTPException(status_code=400, detail="任务名称已存在")
    
    # 检查状态是否合法
    if task.status and task.status not in ["pending", "running", "completed", "failed"]:
        raise HTTPException(status_code=400, detail="不支持的任务状态")
    
    # 更新字段
    update_data = task.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return {"id": db_task.id, "name": db_task.name, "message": "迁移任务更新成功"}

@app.delete("/api/migration_tasks/{task_id}", response_model=dict)
def delete_migration_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(MigrationTask).filter(MigrationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="迁移任务不存在")
    
    db.delete(task)
    db.commit()
    return {"id": task_id, "message": "迁移任务删除成功"}

@app.post("/api/migration_tasks/{task_id}/start", response_model=dict)
def start_migration_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(MigrationTask).filter(MigrationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="迁移任务不存在")
    
    if task.status != "pending":
        raise HTTPException(status_code=400, detail="只有待执行状态的任务才能启动")
    
    # 这里可以添加实际的数据迁移逻辑
    task.status = "running"
    task.progress = 0
    
    # 构建任务描述
    task_description = "任务已开始执行...\n"
    if task.table_names:
        task_description += f"迁移表: {task.table_names}\n"
    else:
        task_description += "迁移表: 所有表\n"
    
    if task.migrate_structure:
        task_description += "包含结构迁移\n"
    else:
        task_description += "不包含结构迁移\n"
    
    if task.migrate_records:
        task_description += "包含记录迁移\n"
    else:
        task_description += "不包含记录迁移\n"
    
    task.log = task_description
    
    db.commit()
    db.refresh(task)
    return {"id": task.id, "status": task.status, "progress": task.progress, "log": task.log, "message": "迁移任务已启动"}

@app.post("/api/migration_tasks/{task_id}/stop", response_model=dict)
def stop_migration_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(MigrationTask).filter(MigrationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="迁移任务不存在")
    
    if task.status != "running":
        raise HTTPException(status_code=400, detail="只有运行中的任务才能停止")
    
    task.status = "failed"
    task.log = task.log + "\n任务已被用户停止"
    
    db.commit()
    db.refresh(task)
    return {"id": task.id, "status": task.status, "log": task.log, "message": "迁移任务已停止"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
