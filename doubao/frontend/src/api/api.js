import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8100/api',
  timeout: 10000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 在发送请求之前做些什么
    return config;
  },
  (error) => {
    // 对请求错误做些什么
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 对响应数据做点什么
    return response.data;
  },
  (error) => {
    // 对响应错误做点什么
    return Promise.reject(error);
  }
);

// 数据源管理API
export const dataSourceApi = {
  // 创建数据源
  createDataSource: (data) => api.post('/data_sources/', data),
  // 获取数据源列表
  getDataSources: () => api.get('/data_sources/'),
  // 获取数据源详情
  getDataSource: (id) => api.get(`/data_sources/${id}`),
  // 更新数据源
  updateDataSource: (id, data) => api.put(`/data_sources/${id}`, data),
  // 删除数据源
  deleteDataSource: (id) => api.delete(`/data_sources/${id}`),
  // 测试连接
  testConnection: (data) => api.post('/data_sources/test_connection', data),
  // 获取数据源表结构
  getDataSourceTables: (id) => api.get(`/data_sources/${id}/tables`),
};

// 迁移任务API
export const migrationTaskApi = {
  // 创建迁移任务
  createMigrationTask: (data) => api.post('/migration_tasks/', data),
  // 获取迁移任务列表
  getMigrationTasks: () => api.get('/migration_tasks/'),
  // 获取迁移任务详情
  getMigrationTask: (id) => api.get(`/migration_tasks/${id}`),
  // 更新迁移任务
  updateMigrationTask: (id, data) => api.put(`/migration_tasks/${id}`, data),
  // 删除迁移任务
  deleteMigrationTask: (id) => api.delete(`/migration_tasks/${id}`),
  // 开始迁移
  startMigration: (id) => api.post(`/migration_tasks/${id}/start`),
  // 获取迁移进度
  getMigrationProgress: (id) => api.get(`/migration_tasks/${id}/progress`),
  // 获取迁移日志
  getMigrationLog: (id) => api.get(`/migration_tasks/${id}/log`),
};

export default api;