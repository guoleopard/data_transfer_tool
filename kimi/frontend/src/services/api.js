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
  try {
    const response = await api.post(`/datasources/test`, config)
    return response.data
  } catch (error) {
    console.error('连接测试失败:', error)
    throw error
  }
}

// 获取数据库表列表
export const getTables = async (datasourceId) => {
  try {
    const response = await api.get(`/datasources/${datasourceId}/tables`)
    return response.data
  } catch (error) {
    console.error('获取表列表失败:', error)
    throw error
  }
}

// 执行迁移任务
export const executeMigration = async (migrationConfig) => {
  try {
    // 首先创建迁移任务
    const createResponse = await api.post('/migration-tasks', {
      name: migrationConfig.name,
      source_datasource_id: migrationConfig.sourceId,
      target_datasource_id: migrationConfig.targetId,
      source_table: migrationConfig.sourceTable,
      target_table: migrationConfig.targetTable,
      description: migrationConfig.description
    })
    
    const task = createResponse.data
    
    // 启动迁移任务
    await api.post(`/migration-tasks/${task.id}/start`)
    
    return {
      success: true,
      taskId: task.id,
      message: '迁移任务已启动'
    }
  } catch (error) {
    console.error('执行迁移任务失败:', error)
    throw error
  }
}

// 获取迁移进度
export const getMigrationProgress = async (taskId) => {
  try {
    const response = await api.get(`/migration-tasks/${taskId}/progress`)
    return response.data
  } catch (error) {
    console.error('获取迁移进度失败:', error)
    throw error
  }
}

// 保存数据源配置
export const saveDataSource = async (dataSource) => {
  try {
    const response = await api.post('/datasources', dataSource)
    return response.data
  } catch (error) {
    console.error('保存数据源失败:', error)
    throw error
  }
}

// 获取已保存的数据源列表
export const getDataSources = async () => {
  try {
    const response = await api.get('/datasources')
    return response.data
  } catch (error) {
    console.error('获取数据源列表失败:', error)
    throw error
  }
}

// 获取数据源详情
export const getDataSource = async (datasourceId) => {
  try {
    const response = await api.get(`/datasources/${datasourceId}`)
    return response.data
  } catch (error) {
    console.error('获取数据源详情失败:', error)
    throw error
  }
}

// 更新数据源
export const updateDataSource = async (datasourceId, dataSource) => {
  try {
    const response = await api.put(`/datasources/${datasourceId}`, dataSource)
    return response.data
  } catch (error) {
    console.error('更新数据源失败:', error)
    throw error
  }
}

// 删除数据源
export const deleteDataSource = async (datasourceId) => {
  try {
    const response = await api.delete(`/datasources/${datasourceId}`)
    return response.data
  } catch (error) {
    console.error('删除数据源失败:', error)
    throw error
  }
}

// 测试数据源连接
export const testDataSourceConnection = async (datasourceId) => {
  try {
    const response = await api.post(`/datasources/${datasourceId}/test`)
    return response.data
  } catch (error) {
    console.error('测试数据源连接失败:', error)
    throw error
  }
}

// 获取表结构
export const getTableStructure = async (datasourceId, tableName) => {
  try {
    const response = await api.get(`/datasources/${datasourceId}/tables/${tableName}/structure`)
    return response.data
  } catch (error) {
    console.error('获取表结构失败:', error)
    throw error
  }
}

// 获取所有迁移任务
export const getMigrationTasks = async () => {
  try {
    const response = await api.get('/migration-tasks')
    return response.data
  } catch (error) {
    console.error('获取迁移任务列表失败:', error)
    throw error
  }
}

// 获取迁移任务详情
export const getMigrationTask = async (taskId) => {
  try {
    const response = await api.get(`/migration-tasks/${taskId}`)
    return response.data
  } catch (error) {
    console.error('获取迁移任务详情失败:', error)
    throw error
  }
}

// 创建迁移任务
export const createMigrationTask = async (taskData) => {
  try {
    const response = await api.post('/migration-tasks', taskData)
    return response.data
  } catch (error) {
    console.error('创建迁移任务失败:', error)
    throw error
  }
}

// 更新迁移任务
export const updateMigrationTask = async (taskId, taskData) => {
  try {
    const response = await api.put(`/migration-tasks/${taskId}`, taskData)
    return response.data
  } catch (error) {
    console.error('更新迁移任务失败:', error)
    throw error
  }
}

// 删除迁移任务
export const deleteMigrationTask = async (taskId) => {
  try {
    const response = await api.delete(`/migration-tasks/${taskId}`)
    return response.data
  } catch (error) {
    console.error('删除迁移任务失败:', error)
    throw error
  }
}

// 启动迁移任务
export const startMigrationTask = async (taskId) => {
  try {
    const response = await api.post(`/migration-tasks/${taskId}/start`)
    return response.data
  } catch (error) {
    console.error('启动迁移任务失败:', error)
    throw error
  }
}

// 取消迁移任务
export const cancelMigrationTask = async (taskId) => {
  try {
    const response = await api.post(`/migration-tasks/${taskId}/cancel`)
    return response.data
  } catch (error) {
    console.error('取消迁移任务失败:', error)
    throw error
  }
}

export default {
  testConnection,
  getTables,
  executeMigration,
  getMigrationProgress,
  saveDataSource,
  getDataSources,
  getDataSource,
  updateDataSource,
  deleteDataSource,
  testDataSourceConnection,
  getTableStructure,
  getMigrationTasks,
  getMigrationTask,
  createMigrationTask,
  updateMigrationTask,
  deleteMigrationTask,
  startMigrationTask,
  cancelMigrationTask
}