import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useDataSourceStore = defineStore('dataSource', () => {
  // 数据源列表
  const dataSources = ref([])
  
  // 当前选中的数据源
  const selectedSource = ref(null)
  const selectedTarget = ref(null)
  
  // 获取所有数据源
  const getAllDataSources = computed(() => dataSources.value)
  
  // 获取可用数据源（已连接的数据源）
  const getAvailableDataSources = computed(() => 
    dataSources.value.filter(ds => ds.status === 'connected')
  )
  
  // 添加数据源
  const addDataSource = (dataSource) => {
    const newDataSource = {
      ...dataSource,
      id: dataSource.id || Date.now().toString(),
      status: dataSource.status || 'unknown',
      createdAt: dataSource.createdAt || new Date().toISOString()
    }
    dataSources.value.push(newDataSource)
    return newDataSource
  }
  
  // 更新数据源
  const updateDataSource = (id, updatedData) => {
    const index = dataSources.value.findIndex(ds => ds.id === id)
    if (index !== -1) {
      dataSources.value[index] = {
        ...dataSources.value[index],
        ...updatedData
      }
      return dataSources.value[index]
    }
    return null
  }
  
  // 删除数据源
  const removeDataSource = (id) => {
    const index = dataSources.value.findIndex(ds => ds.id === id)
    if (index !== -1) {
      dataSources.value.splice(index, 1)
      // 如果删除的是当前选中的数据源，清空选择
      if (selectedSource.value?.id === id) {
        selectedSource.value = null
      }
      if (selectedTarget.value?.id === id) {
        selectedTarget.value = null
      }
      return true
    }
    return false
  }
  
  // 设置数据源状态
  const setDataSourceStatus = (id, status) => {
    const dataSource = dataSources.value.find(ds => ds.id === id)
    if (dataSource) {
      dataSource.status = status
      return true
    }
    return false
  }
  
  // 选择源数据源
  const selectSource = (dataSource) => {
    selectedSource.value = dataSource
  }
  
  // 选择目标数据源
  const selectTarget = (dataSource) => {
    selectedTarget.value = dataSource
  }
  
  // 清空选择
  const clearSelection = () => {
    selectedSource.value = null
    selectedTarget.value = null
  }
  
  // 根据ID获取数据源
  const getDataSourceById = (id) => {
    return dataSources.value.find(ds => ds.id === id)
  }
  
  // 初始化数据源列表
  const initializeDataSources = (sources) => {
    dataSources.value = sources.map(ds => ({
      ...ds,
      status: ds.status || 'unknown'
    }))
  }
  
  return {
    // 状态
    dataSources,
    selectedSource,
    selectedTarget,
    
    // 计算属性
    getAllDataSources,
    getAvailableDataSources,
    
    // 方法
    addDataSource,
    updateDataSource,
    removeDataSource,
    setDataSourceStatus,
    selectSource,
    selectTarget,
    clearSelection,
    getDataSourceById,
    initializeDataSources
  }
})