# 数据迁移工具 - 开发指南

## 项目结构

```
backend/
├── app/                    # 主要应用代码
│   ├── api/               # API路由
│   ├── core/              # 核心配置和数据库连接
│   ├── models/            # 数据库模型
│   ├── schemas/           # Pydantic模型
│   └── services/          # 业务逻辑服务
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量示例
├── main.py               # 应用入口
├── init_db.py            # 数据库初始化
├── setup.py              # 项目信息
└── deploy.sh             # 部署脚本
```

## 开发环境设置

### 1. 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件配置您的数据库连接
```

### 4. 初始化数据库
```bash
python init_db.py
```

### 5. 启动服务
```bash
python main.py
```

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 核心功能

### 数据源管理
- 支持 MySQL、SQL Server、PostgreSQL、SQLite
- 数据源连接测试
- 获取数据库表结构
- 数据源CRUD操作

### 数据迁移任务
- 创建迁移任务
- 启动/取消迁移任务
- 实时进度监控
- 迁移历史记录

## 数据库支持

### MySQL
```python
# 连接字符串格式
mysql://username:password@host:port/database
```

### SQL Server
```python
# 连接字符串格式
mssql+pyodbc://username:password@host:port/database?driver=ODBC+Driver+17+for+SQL+Server
```

### PostgreSQL
```python
# 连接字符串格式
postgresql://username:password@host:port/database
```

### SQLite
```python
# 连接字符串格式
sqlite:///path/to/database.db
```

## 错误处理

所有API端点都包含统一的错误响应格式：

```json
{
  "success": false,
  "message": "错误信息",
  "data": null
}
```

## 日志配置

应用使用结构化日志，支持不同级别的日志输出：

```python
import logging

logger = logging.getLogger(__name__)
logger.info("信息日志")
logger.error("错误日志")
```

## 测试

运行测试：
```bash
python -m pytest
```

## 部署

### 使用部署脚本
```bash
# Windows
deploy.bat

# Linux/Mac
chmod +x deploy.sh
./deploy.sh
```

### 手动部署
1. 安装Python依赖
2. 配置环境变量
3. 初始化数据库
4. 启动服务

## 常见问题

### 数据库连接失败
- 检查数据库服务是否运行
- 验证连接参数是否正确
- 检查网络连接

### 迁移任务卡住
- 查看应用日志获取详细信息
- 检查源数据库和目标数据库状态
- 验证表结构是否兼容

### 性能优化
- 使用连接池
- 批量处理数据
- 监控数据库性能