import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加token等认证信息
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 数据库连接测试
export const testConnection = async (config) => {
  // 模拟API调用延迟
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  // 模拟连接测试结果
  const success = Math.random() > 0.2 // 80%成功率
  
  if (!success) {
    throw new Error('数据库连接失败：请检查连接参数')
  }
  
  return {
    success: true,
    message: '数据库连接成功',
    version: config.dbType === 'mysql' ? '8.0.23' : '2019',
    tables: Math.floor(Math.random() * 50) + 10
  }
}

// 获取数据库表列表
export const getTables = async (config) => {
  await new Promise(resolve => setTimeout(resolve, 800))
  
  const tables = [
    { name: 'users', rows: 1523, size: '2.5MB', comment: '用户表' },
    { name: 'orders', rows: 8456, size: '15.2MB', comment: '订单表' },
    { name: 'products', rows: 234, size: '1.8MB', comment: '产品表' },
    { name: 'categories', rows: 45, size: '256KB', comment: '分类表' },
    { name: 'addresses', rows: 3421, size: '8.3MB', comment: '地址表' },
    { name: 'payments', rows: 6789, size: '12.1MB', comment: '支付记录表' },
    { name: 'inventory', rows: 567, size: '3.2MB', comment: '库存表' },
    { name: 'suppliers', rows: 89, size: '512KB', comment: '供应商表' },
    { name: 'reviews', rows: 2345, size: '4.7MB', comment: '评价表' },
    { name: 'shipments', rows: 1234, size: '2.9MB', comment: '发货表' }
  ]
  
  return {
    success: true,
    data: tables
  }
}

// 执行迁移任务
export const executeMigration = async (migrationConfig) => {
  // 模拟迁移过程
  const totalSteps = 8
  
  for (let step = 0; step < totalSteps; step++) {
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    const progress = Math.round(((step + 1) / totalSteps) * 100)
    
    // 这里可以通过WebSocket或轮询的方式向客户端发送进度更新
    // 现在只是模拟返回最终状态
    if (step === totalSteps - 1) {
      return {
        success: true,
        progress: 100,
        message: '迁移任务完成',
        details: {
          tablesMigrated: migrationConfig.tables.length,
          rowsTransferred: 12453,
          duration: '45秒'
        }
      }
    }
  }
}

// 获取迁移进度
export const getMigrationProgress = async (taskId) => {
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // 模拟进度数据
  const progress = Math.floor(Math.random() * 100)
  
  return {
    success: true,
    progress: progress,
    status: progress < 100 ? 'running' : 'completed',
    logs: [
      { time: new Date().toLocaleTimeString(), message: '正在迁移表结构...', type: 'info' },
      { time: new Date().toLocaleTimeString(), message: '迁移进度更新', type: 'info' }
    ]
  }
}

// 保存数据源配置
export const saveDataSource = async (dataSource) => {
  await new Promise(resolve => setTimeout(resolve, 800))
  
  return {
    success: true,
    data: dataSource
  }
}

// 获取已保存的数据源列表
export const getDataSources = async () => {
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // 模拟数据源数据
  const dataSources = [
    {
      id: '1',
      name: '本地MySQL数据库',
      type: 'mysql',
      host: 'localhost',
      port: 3306,
      username: 'root',
      password: 'password',
      database: 'test_db',
      status: 'connected',
      createdAt: '2024-01-15T10:30:00Z'
    },
    {
      id: '2',
      name: '生产环境SQL Server',
      type: 'sqlserver',
      host: '192.168.1.100',
      port: 1433,
      username: 'sa',
      password: 'admin123',
      database: 'production_db',
      status: 'unknown',
      createdAt: '2024-01-20T14:20:00Z'
    }
  ]
  
  return {
    success: true,
    data: dataSources
  }
}

export default {
  testConnection,
  getTables,
  executeMigration,
  getMigrationProgress,
  saveDataSource,
  getDataSources
}