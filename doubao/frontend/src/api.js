import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8100/api/',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 数据源管理API

export const createDataSource = (data) => {
  return api.post('data_sources/', data);
};

export const getDataSourceList = (params = {}) => {
  return api.get('data_sources/', { params });
};

export const getDataSourceById = (id) => {
  return api.get(`data_sources/${id}`);
};

export const updateDataSource = (id, data) => {
  return api.put(`data_sources/${id}`, data);
};

export const deleteDataSource = (id) => {
  return api.delete(`data_sources/${id}`);
};

// 数据迁移任务管理API

export const createMigrationTask = (data) => {
  return api.post('migration_tasks/', data);
};

export const getMigrationTaskList = (params = {}) => {
  return api.get('migration_tasks/', { params });
};

export const getMigrationTaskById = (id) => {
  return api.get(`migration_tasks/${id}`);
};

export const updateMigrationTask = (id, data) => {
  return api.put(`migration_tasks/${id}`, data);
};

export const deleteMigrationTask = (id) => {
  return api.delete(`migration_tasks/${id}`);
};

export const startMigrationTask = (id) => {
  return api.post(`migration_tasks/${id}/start`);
};

export const stopMigrationTask = (id) => {
  return api.post(`migration_tasks/${id}/stop`);
};

// 导出默认api对象

export default api;