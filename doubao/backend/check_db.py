from sqlalchemy import create_engine, text

# 创建数据库引擎
engine = create_engine('sqlite:///./data_transfer.db')

# 连接数据库并查询
with engine.connect() as conn:
    # 检查data_sources表是否存在
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='data_sources';"))
    table_exists = result.fetchone() is not None
    
    if table_exists:
        print("data_sources表存在")
        # 查询表中的数据
        result = conn.execute(text('SELECT * FROM data_sources'))
        rows = result.all()
        print(f"查询到{len(rows)}条数据:")
        for row in rows:
            print(row)
    else:
        print("data_sources表不存在")

# 关闭连接
engine.dispose()
