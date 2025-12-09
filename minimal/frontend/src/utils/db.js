// 数据库驱动仅在Node.js环境中可用
// import mysql from 'mysql2/promise'
// import sql from 'mssql'

// MySQL连接
export async function connectMySQL(config) {
  try {
    const connection = await mysql.createConnection({
      host: config.host,
      port: config.port,
      user: config.username,
      password: config.password,
      database: config.database
    })
    return { connection, type: 'mysql' }
  } catch (error) {
    throw new Error(`MySQL连接失败: ${error.message}`)
  }
}

// SQL Server连接
export async function connectSQLServer(config) {
  try {
    const pool = await sql.connect({
      server: config.host,
      port: config.port,
      user: config.username,
      password: config.password,
      database: config.database,
      options: {
        encrypt: false
      }
    })
    return { connection: pool, type: 'mssql' }
  } catch (error) {
    throw new Error(`SQL Server连接失败: ${error.message}`)
  }
}

// 获取数据库所有表
export async function getTables(conn, type) {
  try {
    let tables = []
    if (type === 'mysql') {
      const [rows] = await conn.execute(
        'SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()'
      )
      tables = rows.map(row => row.table_name)
    } else if (type === 'mssql') {
      const result = await conn.query(
        "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
      )
      tables = result.recordset.map(row => row.TABLE_NAME)
    }
    return tables
  } catch (error) {
    throw new Error(`获取表列表失败: ${error.message}`)
  }
}

// 获取表结构
export async function getTableSchema(conn, type, tableName) {
  try {
    if (type === 'mysql') {
      const [rows] = await conn.execute(`DESCRIBE ${tableName}`)
      return rows
    } else if (type === 'mssql') {
      const result = await conn.query(`
        SELECT 
          c.COLUMN_NAME, 
          c.DATA_TYPE,
          c.CHARACTER_MAXIMUM_LENGTH,
          c.IS_NULLABLE,
          c.COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS c
        WHERE c.TABLE_NAME = '${tableName}'
        ORDER BY c.ORDINAL_POSITION
      `)
      return result.recordset
    }
  } catch (error) {
    throw new Error(`获取表结构失败: ${error.message}`)
  }
}

// 创建表
export async function createTable(conn, type, tableName, schema, sourceType) {
  try {
    if (type === 'mysql') {
      let sql = `CREATE TABLE ${tableName} (`
      const columns = []
      schema.forEach(col => {
        let columnDef = `${col.Field} ${col.Type}`
        if (col.Null === 'NO') columnDef += ' NOT NULL'
        if (col.Default !== null) columnDef += ` DEFAULT ${col.Default}`
        if (col.Key === 'PRI') columnDef += ' PRIMARY KEY'
        columns.push(columnDef)
      })
      sql += columns.join(', ') + ')'
      await conn.execute(sql)
    } else if (type === 'mssql') {
      let sql = `CREATE TABLE ${tableName} (`
      const columns = []
      schema.forEach(col => {
        let dataType = col.DATA_TYPE
        if (dataType === 'varchar' && col.CHARACTER_MAXIMUM_LENGTH) {
          dataType += `(${col.CHARACTER_MAXIMUM_LENGTH})`
        }
        let columnDef = `[${col.COLUMN_NAME}] ${dataType}`
        if (col.IS_NULLABLE === 'NO') columnDef += ' NOT NULL'
        if (col.COLUMN_DEFAULT !== null) columnDef += ` DEFAULT ${col.COLUMN_DEFAULT}`
        columns.push(columnDef)
      })
      sql += columns.join(', ') + ')'
      await conn.query(sql)
    }
  } catch (error) {
    throw new Error(`创建表失败: ${error.message}`)
  }
}

// 获取表数据总数
export async function getTableCount(conn, type, tableName) {
  try {
    if (type === 'mysql') {
      const [rows] = await conn.execute(`SELECT COUNT(*) as count FROM ${tableName}`)
      return rows[0].count
    } else if (type === 'mssql') {
      const result = await conn.query(`SELECT COUNT(*) as count FROM ${tableName}`)
      return result.recordset[0].count
    }
  } catch (error) {
    throw new Error(`获取表数据总数失败: ${error.message}`)
  }
}

// 分页获取表数据
export async function getTableData(conn, type, tableName, page = 1, pageSize = 1000) {
  try {
    if (type === 'mysql') {
      const offset = (page - 1) * pageSize
      const [rows] = await conn.execute(`SELECT * FROM ${tableName} LIMIT ?, ?`, [offset, pageSize])
      return rows
    } else if (type === 'mssql') {
      const offset = (page - 1) * pageSize
      const result = await conn.query(`
        SELECT * FROM (
            SELECT *, ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) as row_num
            FROM ${tableName}
        ) t
        WHERE row_num > ${offset} AND row_num <= ${offset + pageSize}
      `)
      return result.recordset.map(row => {
        delete row.row_num
        return row
      })
    }
  } catch (error) {
    throw new Error(`获取表数据失败: ${error.message}`)
  }
}

// 插入数据
export async function insertData(conn, type, tableName, data, columns) {
  try {
    if (type === 'mysql') {
      const placeholders = data.map(() => `(${columns.map(() => '?').join(', ')})`).join(', ')
      const values = data.flatMap(row => columns.map(col => row[col]))
      const sql = `INSERT INTO ${tableName} (${columns.join(', ')}) VALUES ${placeholders}`
      await conn.execute(sql, values)
    } else if (type === 'mssql') {
      const placeholders = data.map(() => `(${columns.map((_, i) => `@p${i}`).join(', ')})`).join(', ')
      const sql = `INSERT INTO ${tableName} (${columns.join(', ')}) VALUES ${placeholders}`
      const request = conn.request()
      data.forEach((row, idx) => {
        columns.forEach((col, colIdx) => {
          request.input(`p${colIdx}`, row[col])
        })
      })
      await request.query(sql)
    }
  } catch (error) {
    throw new Error(`插入数据失败: ${error.message}`)
  }
}

// 关闭连接
export async function closeConnection(conn, type) {
  try {
    if (type === 'mysql') {
      await conn.end()
    } else if (type === 'mssql') {
      await conn.close()
    }
  } catch (error) {
    console.error('关闭连接失败:', error)
  }
}