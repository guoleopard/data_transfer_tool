import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8100/api/',
  timeout: 30000,
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加请求头等信息
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

// 数据源管理API
export const dataSourceApi = {
  // 创建数据源
  create: (data) => api.post('data_sources/', data),
  // 获取数据源列表
  list: (params) => api.get('data_sources/', { params }),
  // 获取数据源详情
  get: (id) => api.get(`data_sources/${id}`),
  // 更新数据源
  update: (id, data) => api.put(`data_sources/${id}`, data),
  // 删除数据源
  delete: (id) => api.delete(`data_sources/${id}`),
  // 获取数据源表列表
  getTables: (id) => api.get(`data_sources/${id}/tables`)
};

// 迁移任务管理API
export const migrationTaskApi = {
  // 创建迁移任务
  create: (data) => api.post('migration_tasks/', data),
  // 获取迁移任务列表
  list: (params) => api.get('migration_tasks/', { params }),
  // 获取迁移任务详情
  get: (id) => api.get(`migration_tasks/${id}`),
  // 更新迁移任务
  update: (id, data) => api.put(`migration_tasks/${id}`, data),
  // 删除迁移任务
  delete: (id) => api.delete(`migration_tasks/${id}`),
  // 启动迁移任务
  start: (id) => api.post(`migration_tasks/${id}/start`),
  // 停止迁移任务
  stop: (id) => api.post(`migration_tasks/${id}/stop`),
};

export { api };