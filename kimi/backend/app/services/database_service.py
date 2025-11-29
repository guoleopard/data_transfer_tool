import aiomysql
import aiosqlite
import pyodbc
from typing import Optional, Dict, Any, List
from sqlalchemy import text
import json
import logging

from app.models.models import DatabaseType

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """数据库连接管理器"""
    
    def __init__(self, db_type: DatabaseType, host: str, port: int, 
                 database: str, username: str, password: str):
        self.db_type = db_type
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
    
    async def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            if self.db_type == DatabaseType.MYSQL:
                conn = await aiomysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.username,
                    password=self.password,
                    db=self.database,
                    connect_timeout=10
                )
                conn.close()
                return True
                
            elif self.db_type == DatabaseType.SQLSERVER:
                # SQL Server连接字符串
                conn_str = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={self.host},{self.port};"
                    f"DATABASE={self.database};"
                    f"UID={self.username};"
                    f"PWD={self.password};"
                    f"Connection Timeout=10;"
                )
                conn = pyodbc.connect(conn_str)
                conn.close()
                return True
                
            elif self.db_type == DatabaseType.SQLITE:
                conn = await aiosqlite.connect(self.database)
                await conn.close()
                return True
                
        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}")
            return False
    
    async def get_tables(self) -> List[Dict[str, Any]]:
        """获取数据库中的所有表"""
        try:
            tables = []
            
            if self.db_type == DatabaseType.MYSQL:
                conn = await aiomysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.username,
                    password=self.password,
                    db=self.database
                )
                async with conn.cursor() as cursor:
                    await cursor.execute("SHOW TABLES")
                    result = await cursor.fetchall()
                    tables = [{"name": table[0], "type": "table"} for table in result]
                conn.close()
                
            elif self.db_type == DatabaseType.SQLSERVER:
                conn_str = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={self.host},{self.port};"
                    f"DATABASE={self.database};"
                    f"UID={self.username};"
                    f"PWD={self.password};"
                )
                conn = pyodbc.connect(conn_str)
                cursor = conn.cursor()
                cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
                result = cursor.fetchall()
                tables = [{"name": table[0], "type": "table"} for table in result]
                cursor.close()
                conn.close()
                
            elif self.db_type == DatabaseType.SQLITE:
                conn = await aiosqlite.connect(self.database)
                async with conn.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
                    result = await cursor.fetchall()
                    tables = [{"name": table[0], "type": "table"} for table in result]
                await conn.close()
            
            return tables
            
        except Exception as e:
            logger.error(f"获取表列表失败: {str(e)}")
            return []
    
    async def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表结构"""
        try:
            schema = []
            
            if self.db_type == DatabaseType.MYSQL:
                conn = await aiomysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.username,
                    password=self.password,
                    db=self.database
                )
                async with conn.cursor() as cursor:
                    await cursor.execute(f"DESCRIBE {table_name}")
                    result = await cursor.fetchall()
                    for row in result:
                        schema.append({
                            "column_name": row[0],
                            "data_type": row[1],
                            "is_nullable": row[2] == "YES",
                            "default_value": row[4],
                            "is_primary_key": row[3] == "PRI"
                        })
                conn.close()
                
            elif self.db_type == DatabaseType.SQLSERVER:
                conn_str = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={self.host},{self.port};"
                    f"DATABASE={self.database};"
                    f"UID={self.username};"
                    f"PWD={self.password};"
                )
                conn = pyodbc.connect(conn_str)
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_NAME = '{table_name}'
                """)
                result = cursor.fetchall()
                for row in result:
                    schema.append({
                        "column_name": row[0],
                        "data_type": row[1],
                        "is_nullable": row[2] == "YES",
                        "default_value": row[3],
                        "is_primary_key": False  # 需要额外查询主键信息
                    })
                cursor.close()
                conn.close()
                
            elif self.db_type == DatabaseType.SQLITE:
                conn = await aiosqlite.connect(self.database)
                async with conn.execute(f"PRAGMA table_info({table_name})") as cursor:
                    result = await cursor.fetchall()
                    for row in result:
                        schema.append({
                            "column_name": row[1],
                            "data_type": row[2],
                            "is_nullable": not row[3],
                            "default_value": row[4],
                            "is_primary_key": bool(row[5])
                        })
                await conn.close()
            
            return schema
            
        except Exception as e:
            logger.error(f"获取表结构失败: {str(e)}")
            return []
    
    async def get_table_count(self, table_name: str, filter_condition: Optional[str] = None) -> int:
        """获取表记录数"""
        try:
            count = 0
            
            if self.db_type == DatabaseType.MYSQL:
                conn = await aiomysql.connect(
                    host=self.host,
                    port=self.port,
                    user=self.username,
                    password=self.password,
                    db=self.database
                )
                async with conn.cursor() as cursor:
                    query = f"SELECT COUNT(*) FROM {table_name}"
                    if filter_condition:
                        query += f" WHERE {filter_condition}"
                    await cursor.execute(query)
                    result = await cursor.fetchone()
                    count = result[0] if result else 0
                conn.close()
                
            elif self.db_type == DatabaseType.SQLSERVER:
                conn_str = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={self.host},{self.port};"
                    f"DATABASE={self.database};"
                    f"UID={self.username};"
                    f"PWD={self.password};"
                )
                conn = pyodbc.connect(conn_str)
                cursor = conn.cursor()
                query = f"SELECT COUNT(*) FROM {table_name}"
                if filter_condition:
                    query += f" WHERE {filter_condition}"
                cursor.execute(query)
                result = cursor.fetchone()
                count = result[0] if result else 0
                cursor.close()
                conn.close()
                
            elif self.db_type == DatabaseType.SQLITE:
                conn = await aiosqlite.connect(self.database)
                query = f"SELECT COUNT(*) FROM {table_name}"
                if filter_condition:
                    query += f" WHERE {filter_condition}"
                async with conn.execute(query) as cursor:
                    result = await cursor.fetchone()
                    count = result[0] if result else 0
                await conn.close()
            
            return count
            
        except Exception as e:
            logger.error(f"获取表记录数失败: {str(e)}")
            return 0