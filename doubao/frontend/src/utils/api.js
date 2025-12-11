import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/',
  timeout: 30000
});

// 拦截器：请求拦截
api.interceptors.request.use(
  config => {
    // 可以在这里添加token等请求头信息
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// 拦截器：响应拦截
api.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    // 统一处理错误
    console.error('API请求错误:', error);
    let errorMessage = '请求失败，请稍后重试';
    if (error.response) {
      errorMessage = error.response.data.detail || errorMessage;
    } else if (error.request) {
      errorMessage = '网络连接异常，请检查网络设置';
    }
    return Promise.reject(new Error(errorMessage));
  }
);

// 数据源API
const dataSourceApi = {
  // 创建数据源
  create: (data) => api.post('data_sources/', data),
  // 获取数据源列表
  list: (params) => api.get('data_sources/', { params }),
  // 获取单个数据源
  get: (id) => api.get(`data_sources/${id}`),
  // 更新数据源
  update: (id, data) => api.put(`data_sources/${id}`, data),
  // 删除数据源
  delete: (id) => api.delete(`data_sources/${id}`)
};

// 迁移任务API
const migrationTaskApi = {
  // 创建迁移任务
  create: (data) => api.post('migration_tasks/', data),
  // 获取迁移任务列表
  list: (params) => api.get('migration_tasks/', { params }),
  // 获取单个迁移任务
  get: (id) => api.get(`migration_tasks/${id}`),
  // 更新迁移任务
  update: (id, data) => api.put(`migration_tasks/${id}`, data),
  // 删除迁移任务
  delete: (id) => api.delete(`migration_tasks/${id}`),
  // 启动迁移任务
  start: (id) => api.post(`migration_tasks/${id}/start`),
  // 停止迁移任务
  stop: (id) => api.post(`migration_tasks/${id}/stop`)
};

export { dataSourceApi, migrationTaskApi };
