# 数据迁移工具 - API文档

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证**: 当前版本无需认证
- **数据格式**: JSON
- **响应格式**: 统一响应格式

## 统一响应格式

所有API响应都遵循以下格式：

```json
{
  "success": true,
  "message": "操作成功",
  "data": {}
}
```

## 数据源管理API

### 1. 获取所有数据源

**GET** `/datasources`

**响应示例**:
```json
{
  "success": true,
  "message": "数据源列表获取成功",
  "data": [
    {
      "id": 1,
      "name": "MySQL数据库",
      "db_type": "mysql",
      "host": "localhost",
      "port": 3306,
      "database": "test_db",
      "username": "root",
      "description": "测试数据库",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00"
    }
  ]
}
```

### 2. 获取数据源详情

**GET** `/datasources/{datasource_id}`

**路径参数**:
- `datasource_id`: 数据源ID (整数)

**响应示例**:
```json
{
  "success": true,
  "message": "数据源详情获取成功",
  "data": {
    "id": 1,
    "name": "MySQL数据库",
    "db_type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "test_db",
    "username": "root",
    "description": "测试数据库",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### 3. 创建数据源

**POST** `/datasources`

**请求体**:
```json
{
  "name": "新数据源",
  "db_type": "mysql",
  "host": "localhost",
  "port": 3306,
  "database": "new_db",
  "username": "root",
  "password": "password",
  "description": "新创建的数据源"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "数据源创建成功",
  "data": {
    "id": 2,
    "name": "新数据源",
    "db_type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "new_db",
    "username": "root",
    "description": "新创建的数据源",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00"
  }
}
```

### 4. 更新数据源

**PUT** `/datasources/{datasource_id}`

**路径参数**:
- `datasource_id`: 数据源ID (整数)

**请求体**:
```json
{
  "name": "更新后的数据源",
  "host": "192.168.1.100",
  "port": 3306,
  "database": "updated_db",
  "username": "root",
  "password": "new_password",
  "description": "更新后的描述"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "数据源更新成功",
  "data": {
    "id": 1,
    "name": "更新后的数据源",
    "db_type": "mysql",
    "host": "192.168.1.100",
    "port": 3306,
    "database": "updated_db",
    "username": "root",
    "description": "更新后的描述",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### 5. 删除数据源

**DELETE** `/datasources/{datasource_id}`

**路径参数**:
- `datasource_id`: 数据源ID (整数)

**响应示例**:
```json
{
  "success": true,
  "message": "数据源删除成功",
  "data": null
}
```

### 6. 测试数据源连接

**POST** `/datasources/{datasource_id}/test`

**路径参数**:
- `datasource_id`: 数据源ID (整数)

**响应示例**:
```json
{
  "success": true,
  "message": "数据库连接成功",
  "data": {
    "connected": true,
    "server_version": "8.0.23",
    "database": "test_db"
  }
}
```

### 7. 获取数据源表列表

**GET** `/datasources/{datasource_id}/tables`

**路径参数**:
- `datasource_id`: 数据源ID (整数)

**响应示例**:
```json
{
  "success": true,
  "message": "表列表获取成功",
  "data": [
    {
      "name": "users",
      "schema": "public",
      "type": "table",
      "row_count": 1000
    },
    {
      "name": "orders",
      "schema": "public",
      "type": "table",
      "row_count": 5000
    }
  ]
}
```

### 8. 获取表结构

**GET** `/datasources/{datasource_id}/tables/{table_name}/structure`

**路径参数**:
- `datasource_id`: 数据源ID (整数)
- `table_name`: 表名 (字符串)

**响应示例**:
```json
{
  "success": true,
  "message": "表结构获取成功",
  "data": {
    "columns": [
      {
        "name": "id",
        "type": "INTEGER",
        "nullable": false,
        "primary_key": true,
        "default": null
      },
      {
        "name": "name",
        "type": "VARCHAR(100)",
        "nullable": false,
        "primary_key": false,
        "default": null
      }
    ],
    "indexes": [
      {
        "name": "PRIMARY",
        "columns": ["id"],
        "unique": true
      }
    ]
  }
}
```

## 迁移任务API

### 1. 获取所有迁移任务

**GET** `/migration-tasks`

**响应示例**:
```json
{
  "success": true,
  "message": "迁移任务列表获取成功",
  "data": [
    {
      "id": 1,
      "name": "用户数据迁移",
      "source_datasource_id": 1,
      "target_datasource_id": 2,
      "source_table": "users",
      "target_table": "users",
      "status": "completed",
      "progress": 100,
      "total_rows": 1000,
      "migrated_rows": 1000,
      "started_at": "2024-01-01T10:00:00",
      "completed_at": "2024-01-01T10:05:00",
      "created_at": "2024-01-01T09:00:00"
    }
  ]
}
```

### 2. 获取迁移任务详情

**GET** `/migration-tasks/{task_id}`

**路径参数**:
- `task_id`: 迁移任务ID (整数)

**响应示例**:
```json
{
  "success": true,
  "message": "迁移任务详情获取成功",
  "data": {
    "id": 1,
    "name": "用户数据迁移",
    "source_datasource_id": 1,
    "target_datasource_id": 2,
    "source_table": "users",
    "target_table": "users",
    "status": "completed",
    "progress": 100,
    "total_rows": 1000,
    "migrated_rows": 1000,
    "started_at": "2024-01-01T10:00:00",
    "completed_at": "2024-01-01T10:05:00",
    "created_at": "2024-01-01T09:00:00"
  }
}
```

### 3. 创建迁移任务

**POST** `/migration-tasks`

**请求体**:
```json
{
  "name": "新迁移任务",
  "source_datasource_id": 1,
  "target_datasource_id": 2,
  "source_table": "products",
  "target_table": "products",
  "description": "产品数据迁移"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "迁移任务创建成功",
  "data": {
    "id": 2,
    "name": "新迁移任务",
    "source_datasource_id": 1,
    "target_datasource_id": 2,
    "source_table": "products",
    "target_table": "products",
    "status": "pending",
    "progress": 0,
    "total_rows": 0,
    "migrated_rows": 0,
    "created_at": "2024-01-01T13:00:00"
  }
}
```

### 4. 更新迁移任务

**PUT** `/migration-tasks/{task_id}`

**路径参数**:
- `task_id`: 迁移任务ID (整数)

**请求体**:
```json
{
  "name": "更新的迁移任务",
  "description": "更新描述"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "迁移任务更新成功",
  "data": {
    "id": 2,
    "name": "更新的迁移任务",
    "source_datasource_id": 1,
    "target_datasource_id": 2,
    "source_table": "products",
    "target_table": "products",
    "status": "pending",
    "progress": 0,
    "description": "更新描述",
    "created_at": "2024-01-01T13:00:00"
  }
}
```

### 5. 删除迁移任务

**DELETE** `/migration-tasks/{task_id}`

**路径参数**:
- `task_id`: 迁移任务ID (整数)

**响应示例**:
```json
{
  "success": true,
  "message": "迁移任务删除成功",
  "data": null
}
```

### 6. 启动迁移任务

**POST** `/migration-tasks/{task_id}/start`

**路径参数**:
- `task_id`: 迁移任务ID (整数)

**响应示例**:
```json
{
  "success": true,
  "message": "迁移任务启动成功",
  "data": {
    "id": 2,
    "status": "running",
    "started_at": "2024-01-01T14:00:00"
  }
}
```

### 7. 取消迁移任务

**POST** `/migration-tasks/{task_id}/cancel`

**路径参数**:
- `task_id`: 迁移任务ID (整数)

**响应示例**:
```json
{
  "success": true,
  "message": "迁移任务取消成功",
  "data": {
    "id": 2,
    "status": "cancelled",
    "completed_at": "2024-01-01T14:30:00"
  }
}
```

### 8. 获取迁移任务进度

**GET** `/migration-tasks/{task_id}/progress`

**路径参数**:
- `task_id`: 迁移任务ID (整数)

**响应示例**:
```json
{
  "success": true,
  "message": "迁移进度获取成功",
  "data": {
    "id": 2,
    "status": "running",
    "progress": 75,
    "total_rows": 1000,
    "migrated_rows": 750,
    "current_table": "products",
    "estimated_time_remaining": "2分钟"
  }
}
```

## 错误响应

所有API在出错时都会返回如下格式的错误响应：

```json
{
  "success": false,
  "message": "错误描述信息",
  "data": null
}
```

**常见错误码**:
- `400`: 请求参数错误
- `404`: 资源未找到
- `500`: 服务器内部错误
- `422`: 数据验证错误

## 使用示例

### Python示例

```python
import requests

# 基础配置
base_url = "http://localhost:8000/api/v1"

# 创建数据源
data = {
    "name": "测试数据库",
    "db_type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "test_db",
    "username": "root",
    "password": "password",
    "description": "测试数据源"
}

response = requests.post(f"{base_url}/datasources", json=data)
result = response.json()
print(result)
```

### cURL示例

```bash
# 创建数据源
curl -X POST "http://localhost:8000/api/v1/datasources" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试数据库",
    "db_type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "test_db",
    "username": "root",
    "password": "password",
    "description": "测试数据源"
  }'
```