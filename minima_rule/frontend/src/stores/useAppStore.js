import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 数据源列表
  const datasources = ref([])

  // 从本地存储加载数据源
  const loadDatasources = () => {
    const saved = localStorage.getItem('datasources')
    if (saved) {
      datasources.value = JSON.parse(saved)
    }
  }

  // 保存数据源到本地存储
  const saveDatasources = () => {
    localStorage.setItem('datasources', JSON.stringify(datasources.value))
  }

  // 添加数据源
  const addDatasource = (datasource) => {
    datasources.value.push({
      ...datasource,
      id: Date.now()
    })
    saveDatasources()
  }

  // 更新数据源
  const updateDatasource = (id, datasource) => {
    const index = datasources.value.findIndex(item => item.id === id)
    if (index !== -1) {
      datasources.value[index] = { ...datasource, id }
      saveDatasources()
    }
  }

  // 删除数据源
  const deleteDatasource = (id) => {
    datasources.value = datasources.value.filter(item => item.id !== id)
    saveDatasources()
  }

  return {
    datasources,
    loadDatasources,
    addDatasource,
    updateDatasource,
    deleteDatasource
  }
})