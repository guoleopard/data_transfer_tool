# 数据迁移工具 - 后端服务

基于FastAPI的数据迁移工具后端服务，支持MySQL和SQL Server数据库。

## 功能特性

- ✅ 数据源管理（支持MySQL、SQL Server、SQLite）
- ✅ 数据迁移任务管理
- ✅ 异步任务处理
- ✅ RESTful API接口
- ✅ 数据库连接测试
- ✅ 表结构查看
- ✅ 任务进度监控
- ✅ 支持字段映射配置
- ✅ 支持数据过滤条件

## 技术栈

- **框架**: FastAPI
- **数据库**: SQLAlchemy (支持异步)
- **数据库驱动**: aiomysql, pyodbc, aiosqlite
- **配置管理**: pydantic-settings
- **API文档**: 自动生成Swagger和ReDoc

## 环境要求

- Python 3.8+
- MySQL 5.7+ (可选)
- SQL Server 2016+ (可选)

## 快速开始

### 1. 创建虚拟环境
```bash
cd backend
python -m venv venv
```

### 2. 激活虚拟环境
Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

### 5. 运行服务
```bash
python main.py
```

服务启动后：
- API服务: http://localhost:8000
- Swagger文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc

## API端点

### 数据源管理

- `POST /api/datasources` - 创建数据源
- `GET /api/datasources` - 获取数据源列表
- `GET /api/datasources/{id}` - 获取单个数据源
- `PUT /api/datasources/{id}` - 更新数据源
- `DELETE /api/datasources/{id}` - 删除数据源
- `POST /api/datasources/{id}/test` - 测试数据源连接
- `GET /api/datasources/{id}/tables` - 获取数据源表列表
- `GET /api/datasources/{id}/tables/{table}/schema` - 获取表结构

### 迁移任务管理

- `POST /api/migration-tasks` - 创建迁移任务
- `GET /api/migration-tasks` - 获取任务列表
- `GET /api/migration-tasks/{id}` - 获取单个任务
- `PUT /api/migration-tasks/{id}` - 更新任务
- `DELETE /api/migration-tasks/{id}` - 删除任务
- `POST /api/migration-tasks/{id}/start` - 启动任务
- `POST /api/migration-tasks/{id}/cancel` - 取消任务
- `GET /api/migration-tasks/{id}/progress` - 获取任务进度

## 项目结构

```
backend/
├── app/
│   ├── api/              # API路由
│   │   ├── __init__.py
│   │   ├── routes.py     # 主路由文件
│   │   └── api.py
│   ├── core/             # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py     # 配置管理
│   │   └── database.py   # 数据库连接
│   ├── models/           # 数据模型
│   │   ├── __init__.py
│   │   └── models.py     # SQLAlchemy模型
│   ├── schemas/          # Pydantic模型
│   │   ├── __init__.py
│   │   └── schemas.py    # 请求/响应模型
│   └── services/         # 业务逻辑
│       ├── database_service.py   # 数据库连接服务
│       ├── datasource_service.py # 数据源服务
│       └── migration_service.py  # 迁移任务服务
├── main.py               # 应用入口
├── requirements.txt      # 依赖包
├── .env.example          # 环境变量示例
└── README.md            # 项目说明
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| APP_NAME | 应用名称 | 数据迁移工具 |
| DEBUG | 调试模式 | true |
| HOST | 服务地址 | 0.0.0.0 |
| PORT | 服务端口号 | 8000 |
| DATABASE_URL | 数据库连接URL | sqlite+aiosqlite:///./data_transfer.db |
| ALLOWED_HOSTS | CORS允许的域名 | ["http://localhost:3000", "http://localhost:5173"] |
| MAX_CONCURRENT_TASKS | 最大并发任务数 | 3 |
| TASK_TIMEOUT | 任务超时时间(秒) | 3600 |

### 数据库连接示例

**SQLite** (默认):
```
DATABASE_URL=sqlite+aiosqlite:///./data_transfer.db
```

**MySQL**:
```
DATABASE_URL=mysql+aiomysql://username:password@localhost:3306/data_transfer
```

**PostgreSQL**:
```
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/data_transfer
```

## 使用示例

### 创建数据源
```bash
curl -X POST "http://localhost:8000/api/datasources" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MySQL数据源",
    "description": "测试MySQL数据库",
    "db_type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "test_db",
    "username": "root",
    "password": "password",
    "is_active": true
  }'
```

### 创建迁移任务
```bash
curl -X POST "http://localhost:8000/api/migration-tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "用户表迁移",
    "description": "迁移用户表数据",
    "source_id": 1,
    "target_id": 2,
    "source_table": "users",
    "target_table": "users",
    "mapping_config": "{}",
    "filter_condition": "status = 1"
  }'
```

### 启动迁移任务
```bash
curl -X POST "http://localhost:8000/api/migration-tasks/1/start"
```

### 查看任务进度
```bash
curl "http://localhost:8000/api/migration-tasks/1/progress"
```

## 开发计划

- [ ] 支持更多数据库类型 (PostgreSQL, Oracle)
- [ ] 数据同步功能
- [ ] 任务调度功能
- [ ] 数据转换规则配置
- [ ] 增量数据迁移
- [ ] 数据校验功能
- [ ] Web界面管理

## 许可证

MIT License