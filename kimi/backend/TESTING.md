# 数据迁移工具 - 测试指南

## 测试环境设置

### 1. 安装测试依赖

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx
```

### 2. 创建测试数据库

```bash
# 创建测试数据库
sqlite3 test.db "VACUUM;"

# 或者使用内存数据库进行测试
```

## 单元测试

### 测试结构

```
tests/
├── __init__.py
├── conftest.py              # 测试配置
├── test_database.py          # 数据库测试
├── test_services.py          # 服务测试
├── test_api.py              # API测试
└── test_models.py           # 模型测试
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api.py

# 运行特定测试函数
pytest tests/test_api.py::test_create_datasource

# 显示详细信息
pytest -v

# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 显示测试输出
pytest -s
```

## 测试用例

### 数据库连接测试

```python
# tests/test_database.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, init_db

@pytest.mark.asyncio
async def test_database_connection():
    """测试数据库连接"""
    async for db in get_db():
        result = await db.execute("SELECT 1")
        assert result.scalar() == 1

@pytest.mark.asyncio
async def test_database_init():
    """测试数据库初始化"""
    await init_db()
    # 验证表是否创建
    async for db in get_db():
        result = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in result.fetchall()]
        assert 'datasources' in tables
        assert 'migration_tasks' in tables
```

### 数据源服务测试

```python
# tests/test_services.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.datasource_service import DataSourceService
from app.schemas import DataSourceCreate

@pytest.mark.asyncio
async def test_create_datasource(db_session: AsyncSession):
    """测试创建数据源"""
    service = DataSourceService(db_session)
    
    datasource_data = DataSourceCreate(
        name="测试数据库",
        db_type="mysql",
        host="localhost",
        port=3306,
        database="test_db",
        username="root",
        password="password",
        description="测试数据源"
    )
    
    result = await service.create_datasource(datasource_data)
    
    assert result.name == "测试数据库"
    assert result.db_type == "mysql"
    assert result.host == "localhost"
    assert result.is_active is True

@pytest.mark.asyncio
async def test_test_connection(db_session: AsyncSession):
    """测试数据源连接"""
    service = DataSourceService(db_session)
    
    # 创建测试数据源
    datasource_data = DataSourceCreate(
        name="SQLite测试",
        db_type="sqlite",
        database=":memory:",
        description="内存数据库测试"
    )
    
    datasource = await service.create_datasource(datasource_data)
    
    # 测试连接
    result = await service.test_connection(datasource.id)
    
    assert result["connected"] is True
    assert "server_version" in result
```

### API测试

```python
# tests/test_api.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_create_datasource_api():
    """测试创建数据源API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/datasources",
            json={
                "name": "API测试数据库",
                "db_type": "sqlite",
                "database": ":memory:",
                "description": "API测试"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "API测试数据库"

@pytest.mark.asyncio
async def test_get_datasources_api():
    """测试获取数据源列表API"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/datasources")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查端点"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
```

## 集成测试

### 完整迁移流程测试

```python
# tests/test_integration.py
import pytest
import asyncio
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_full_migration_workflow():
    """测试完整的迁移流程"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. 创建源数据源
        source_response = await client.post(
            "/api/v1/datasources",
            json={
                "name": "源数据库",
                "db_type": "sqlite",
                "database": "source.db",
                "description": "源数据库"
            }
        )
        source_id = source_response.json()["data"]["id"]
        
        # 2. 创建目标数据源
        target_response = await client.post(
            "/api/v1/datasources",
            json={
                "name": "目标数据库",
                "db_type": "sqlite",
                "database": "target.db",
                "description": "目标数据库"
            }
        )
        target_id = target_response.json()["data"]["id"]
        
        # 3. 创建迁移任务
        task_response = await client.post(
            "/api/v1/migration-tasks",
            json={
                "name": "测试迁移任务",
                "source_datasource_id": source_id,
                "target_datasource_id": target_id,
                "source_table": "users",
                "target_table": "users",
                "description": "测试迁移"
            }
        )
        task_id = task_response.json()["data"]["id"]
        
        # 4. 启动迁移任务
        start_response = await client.post(f"/api/v1/migration-tasks/{task_id}/start")
        assert start_response.status_code == 200
        
        # 5. 检查任务状态
        status_response = await client.get(f"/api/v1/migration-tasks/{task_id}")
        assert status_response.status_code == 200
        
        task_data = status_response.json()["data"]
        assert task_data["status"] in ["running", "completed"]
```

## 性能测试

### 数据库连接池测试

```python
# tests/test_performance.py
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from app.services.database_service import DatabaseConnection

@pytest.mark.asyncio
async def test_connection_pool_performance():
    """测试连接池性能"""
    db_conn = DatabaseConnection(
        db_type="sqlite",
        database=":memory:"
    )
    
    start_time = time.time()
    
    # 并发测试
    tasks = []
    for i in range(100):
        task = asyncio.create_task(db_conn.test_connection())
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # 验证所有连接都成功
    assert all(result["connected"] for result in results)
    
    # 验证性能（100次连接应该在5秒内完成）
    assert duration < 5.0
    
    print(f"100次连接测试完成，耗时: {duration:.2f}秒")
```

### 大数据量迁移测试

```python
# tests/test_bulk_migration.py
import pytest
import asyncio
from app.services.migration_service import MigrationTaskService
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_bulk_data_migration(db_session: AsyncSession):
    """测试大数据量迁移"""
    service = MigrationTaskService(db_session)
    
    # 创建测试数据（10000条记录）
    # ... 创建测试数据代码 ...
    
    # 执行迁移
    start_time = time.time()
    
    # 模拟迁移任务
    migration_result = await service.execute_migration(
        task_id=1,
        batch_size=1000
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    # 验证迁移结果
    assert migration_result["status"] == "completed"
    assert migration_result["total_rows"] == 10000
    assert migration_result["migrated_rows"] == 10000
    
    # 验证性能（10000条记录应该在30秒内完成）
    assert duration < 30.0
    
    print(f"10000条记录迁移完成，耗时: {duration:.2f}秒")
```

## 测试数据准备

### 测试数据库初始化

```python
# tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.database import Base, get_db
from app.models import DataSource, MigrationTask, DatabaseType, TaskStatus

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine) -> AsyncSession:
    """创建测试数据库会话"""
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()

@pytest.fixture
async def sample_datasource(db_session: AsyncSession):
    """创建示例数据源"""
    datasource = DataSource(
        name="测试数据源",
        db_type=DatabaseType.SQLITE,
        database=":memory:",
        description="测试用数据源"
    )
    db_session.add(datasource)
    await db_session.commit()
    await db_session.refresh(datasource)
    return datasource

@pytest.fixture
async def sample_migration_task(db_session: AsyncSession, sample_datasource):
    """创建示例迁移任务"""
    task = MigrationTask(
        name="测试迁移任务",
        source_datasource_id=sample_datasource.id,
        target_datasource_id=sample_datasource.id,
        source_table="test_table",
        target_table="test_table",
        status=TaskStatus.PENDING
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task
```

## 测试报告

### 生成测试报告

```bash
# 生成HTML格式测试报告
pytest --html=report.html --self-contained-html

# 生成XML格式测试报告
pytest --junitxml=report.xml

# 生成覆盖率报告
pytest --cov=app --cov-report=html --cov-report=term

# 生成所有类型的报告
pytest --html=report.html --cov=app --cov-report=html --cov-report=term-missing
```

### 测试结果分析

```bash
# 运行测试并显示统计信息
pytest --tb=short -v

# 只运行失败的测试
pytest --lf

# 运行上次失败的测试，然后运行其他测试
pytest --ff

# 并行运行测试（需要安装pytest-xdist）
pytest -n auto
```

## 持续集成

### GitHub Actions配置

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```