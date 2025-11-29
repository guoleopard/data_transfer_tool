# 数据迁移工具 - Docker支持

## Docker化部署

### 构建镜像

```bash
# 构建后端镜像
docker build -t data-migration-backend .

# 或者使用docker-compose
docker-compose build
```

### 运行容器

```bash
# 使用docker-compose（推荐）
docker-compose up -d

# 或者单独运行后端
docker run -d -p 8000:8000 --name data-migration-backend data-migration-backend
```

### 查看日志

```bash
# 查看容器日志
docker logs data-migration-backend

# 实时查看日志
docker logs -f data-migration-backend
```

### 停止容器

```bash
# 使用docker-compose
docker-compose down

# 或者单独停止
docker stop data-migration-backend
```

## 环境变量配置

Docker容器支持以下环境变量：

```yaml
# 应用配置
APP_NAME=数据迁移工具
APP_VERSION=1.0.0
DEBUG=false

# 数据库配置
DATABASE_URL=sqlite:///./app.db
# 或者
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password
DB_NAME=data_migration

# CORS配置
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json

# 连接池配置
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_PRE_PING=true
DB_POOL_RECYCLE=3600

# 迁移配置
MIGRATION_BATCH_SIZE=1000
MIGRATION_MAX_WORKERS=4
```

## Docker Compose配置

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
      - DEBUG=false
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # 可选：PostgreSQL数据库
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: data_migration
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  # 可选：MySQL数据库
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: data_migration
      MYSQL_ROOT_PASSWORD: password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped

volumes:
  postgres_data:
  mysql_data:
```

## 生产环境部署

### 使用环境变量文件

```bash
# 创建环境变量文件
cp .env.example .env.production

# 编辑生产环境配置
vim .env.production

# 使用生产环境配置运行
docker-compose --env-file .env.production up -d
```

### 使用外部数据库

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@external-db:5432/data_migration
      - DEBUG=false
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - app-network

networks:
  app-network:
    external: true
```

### 使用反向代理

```yaml
# docker-compose.nginx.yml
version: '3.8'

services:
  backend:
    build: .
    expose:
      - "8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
    restart: unless-stopped
```

## 监控和日志

### 健康检查

应用提供健康检查端点：

```bash
# 检查应用健康状态
curl http://localhost:8000/health

# 响应示例
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0",
  "database": "connected"
}
```

### 日志管理

```bash
# 查看实时日志
docker logs -f data-migration-backend

# 导出日志
docker logs data-migration-backend > app.log 2>&1

# 使用日志驱动
docker run -d \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  data-migration-backend
```

## 备份和恢复

### 数据库备份

```bash
# SQLite备份
docker exec data-migration-backend sqlite3 /app/app.db ".backup /backup/app_backup.db"

# PostgreSQL备份
docker exec postgres pg_dump -U postgres data_migration > backup.sql

# MySQL备份
docker exec mysql mysqldump -u root -p data_migration > backup.sql
```

### 数据恢复

```bash
# SQLite恢复
docker exec -i data-migration-backend sqlite3 /app/app.db < backup.sql

# PostgreSQL恢复
docker exec -i postgres psql -U postgres data_migration < backup.sql

# MySQL恢复
docker exec -i mysql mysql -u root -p data_migration < backup.sql
```

## 性能优化

### 环境变量优化

```yaml
# 生产环境优化配置
environment:
  - WORKERS=4                    # 工作进程数
  - WORKER_TIMEOUT=300          # 工作进程超时时间
  - KEEP_ALIVE=2                # 保持连接时间
  - MAX_REQUESTS=1000           # 最大请求数
  - MAX_REQUESTS_JITTER=50      # 请求数抖动
```

### 资源限制

```yaml
# 资源限制
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '1.0'
      memory: 1G
```