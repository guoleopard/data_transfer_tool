<template>
  <div class="migration-task">
    <h3>迁移任务配置</h3>
    <div class="task-config">
      <div class="config-row">
        <div class="config-group">
          <label>源数据库</label>
          <input type="text" :value="sourceConfig ? `${sourceConfig.dbType || sourceConfig.type} - ${sourceConfig.database}` : '未配置'" :disabled="readonlySources || readonlyAll" />
        </div>
        <div class="config-group">
          <label>目标数据库</label>
          <input type="text" :value="targetConfig ? `${targetConfig.dbType || targetConfig.type} - ${targetConfig.database}` : '未配置'" :disabled="readonlySources || readonlyAll" />
        </div>
      </div>
      
      <div v-if="sourceTables.length > 0" class="tables-section">
        <label>选择需要迁移的表</label>
        <div class="table-selector">
          <div class="table-group">
            <label>
              <input type="checkbox" @change="selectAllTables" v-model="selectAll" />
              全选
            </label>
          </div>
          <div v-for="table in sourceTables" :key="table" class="table-group">
            <label>
              <input type="checkbox" v-model="selectedTables" :value="table" />
              {{ table }}
            </label>
          </div>
        </div>
      </div>

      <div class="migration-type">
        <label>迁移类型</label>
        <div class="type-options">
          <label>
            <input type="radio" v-model="migrationMode" value="structure" />
            仅结构迁移
          </label>
          <label>
            <input type="radio" v-model="migrationMode" value="data" />
            仅数据迁移
          </label>
          <label>
            <input type="radio" v-model="migrationMode" value="both" />
            结构+数据迁移
          </label>
        </div>
      </div>

      <div v-if="!readonlyAll" class="task-actions">
        <button 
          class="config-btn" 
          @click="saveMigrationTask"
          :disabled="selectedTables.value.length === 0 || taskConfigured.value"
        >
          {{ taskConfigured.value ? '任务已保存' : '保存迁移任务' }}
        </button>
        <button 
          class="start-btn" 
          @click="startMigration"
          :disabled="!canStartMigration"
        >
          {{ migrating ? '迁移中...' : '开始迁移' }}
        </button>
      </div>
    </div>

    <div v-if="progressVisible" class="progress-section">
      <h4>迁移进度</h4>
      <div class="progress-item" v-for="(progress, table) in migrationProgress" :key="table">
        <div class="progress-header">
          <span>{{ table }}</span>
          <span>{{ progress.status }}</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress.percentage + '%' }"></div>
        </div>
        <span class="progress-text">{{ progress.message }}</span>
      </div>
      <div v-if="migrationComplete" class="complete-message">
        <div :class="['message', migrationSuccess ? 'success' : 'error']">
          {{ migrationSuccess ? '迁移任务已完成!' : '迁移过程中发生错误!' }}
        </div>
        <button @click="resetMigration">重置任务</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineProps, defineEmits } from 'vue'

const props = defineProps({
  sourceConfig: Object,
  targetConfig: Object,
  readonlySources: { type: Boolean, default: false },
  readonlyAll: { type: Boolean, default: false },
  autoStart: { type: Boolean, default: false }
})

const emit = defineEmits(['migration-complete', 'task-created'])

const sourceTables = ref(['users', 'posts', 'comments', 'products', 'orders'])
const selectedTables = ref([])
const selectAll = ref(false)
const migrationMode = ref('both')
const migrating = ref(false)
const migrationProgress = ref({})
const progressVisible = ref(false)
const migrationComplete = ref(false)
const migrationSuccess = ref(false)
const taskConfigured = ref(false)

const readonlySources = computed(() => props.readonlySources || props.readonlyAll)
const readonlyAll = computed(() => props.readonlyAll)

const canStartMigration = computed(() => {
  return props.sourceConfig && props.targetConfig && selectedTables.value.length > 0 && !migrating.value && taskConfigured.value
})

// 自动加载表
if (props.sourceConfig) {
  sourceTables.value = ['users', 'posts', 'comments', 'products', 'orders']
}

const selectAllTables = () => {
  if (selectAll.value) {
    selectedTables.value = [...sourceTables.value]
  } else {
    selectedTables.value = []
  }
}

const saveMigrationTask = () => {
  if (selectedTables.value.length === 0) return
  
  taskConfigured.value = true
  
  emit('task-created', {
    sourceConfig: props.sourceConfig,
    targetConfig: props.targetConfig,
    migrationType: migrationMode.value,
    selectedTables: selectedTables.value
  })
}

const startMigration = async () => {
  if (!taskConfigured.value) {
    saveMigrationTask()
  }
  migrating.value = true
  progressVisible.value = true
  migrationComplete.value = false
  migrationSuccess.value = true
  migrationProgress.value = {}

  try {
    for (const table of selectedTables.value) {
      migrationProgress.value[table] = {
        percentage: 0,
        status: '准备中',
        message: '开始处理表: ' + table
      }

      // 模拟结构迁移
      if (migrationMode.value === 'structure' || migrationMode.value === 'both') {
        await new Promise(resolve => setTimeout(resolve, 1000))
        migrationProgress.value[table].status = '结构迁移中'
        migrationProgress.value[table].message = '正在获取表结构'
        migrationProgress.value[table].percentage = 30
        
        await new Promise(resolve => setTimeout(resolve, 1000))
        migrationProgress.value[table].message = '正在创建目标表'
        migrationProgress.value[table].percentage = 60
      }

      // 模拟数据迁移
      if (migrationMode.value === 'data' || migrationMode.value === 'both') {
        await new Promise(resolve => setTimeout(resolve, 500))
        migrationProgress.value[table].status = '数据迁移中'
        migrationProgress.value[table].message = '正在统计数据总量'
        
        const totalCount = 2500
        const pageSize = 1000
        const totalPages = Math.ceil(totalCount / pageSize)
        
        for (let page = 1; page <= totalPages; page++) {
          await new Promise(resolve => setTimeout(resolve, 500))
          const percentage = Math.round(((page / totalPages) * 40) + (migrationMode.value === 'both' ? 60 : 30))
          migrationProgress.value[table].percentage = percentage
          migrationProgress.value[table].message = `正在迁移数据: ${Math.min(page * pageSize, totalCount)}/${totalCount} 条`
        }
      }

      await new Promise(resolve => setTimeout(resolve, 500))
      migrationProgress.value[table].percentage = 100
      migrationProgress.value[table].status = '完成'
      migrationProgress.value[table].message = '迁移完成'
    }
  } catch (error) {
    migrationSuccess.value = false
    // 将当前失败的表标记为错误
    Object.keys(migrationProgress.value).forEach(table => {
      if (migrationProgress.value[table].percentage < 100) {
        migrationProgress.value[table].status = '失败'
        migrationProgress.value[table].message = error.message
      }
    })
  } finally {
    migrating.value = false
    migrationComplete.value = true
    emit('migration-complete')
  }
}

// 自动启动迁移
if (props.autoStart && props.sourceConfig && props.targetConfig) {
  setTimeout(() => {
    selectAll.value = true
    selectAllTables()
    saveMigrationTask()
    setTimeout(() => {
      startMigration()
    }, 500)
  }, 500)
}

const resetMigration = () => {
  migrationProgress.value = {}
  progressVisible.value = false
  migrationComplete.value = false
  migrationSuccess.value = false
}
</script>

<style scoped>
.migration-task {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  background: #fff;
  margin-top: 20px;
}

.migration-task h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
}

.task-config {
  margin-bottom: 30px;
}

.config-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.config-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.config-group label {
  font-weight: 500;
  color: #555;
}

.config-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.tables-section {
  margin-bottom: 20px;
}

.tables-section label {
  display: block;
  margin-bottom: 10px;
  font-weight: 500;
  color: #555;
}

.table-selector {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  background: #fafafa;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
}

.table-group {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.migration-type {
  margin-bottom: 20px;
}

.migration-type label {
  display: block;
  margin-bottom: 10px;
  font-weight: 500;
  color: #555;
}

.type-options {
  display: flex;
  gap: 20px;
}

.type-options label {
  cursor: pointer;
  font-weight: normal;
}

.task-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.config-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.config-btn:not(:disabled):hover {
  background: #059669;
}

.config-btn:disabled {
  background: #6ee7b7;
  cursor: not-allowed;
}

.start-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.start-btn:not(:disabled):hover {
  background: #2563eb;
}

.start-btn:disabled {
  background: #93c5fd;
  cursor: not-allowed;
}

.progress-section h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.progress-item {
  margin-bottom: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 14px;
  font-weight: 500;
}

.progress-bar {
  height: 20px;
  border: 1px solid #ddd;
  border-radius: 10px;
  overflow: hidden;
  background: #f5f5f5;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #42b983, #359469);
  transition: width 0.3s ease;
}

.progress-text {
  display: block;
  margin-top: 5px;
  font-size: 12px;
  color: #666;
}

.complete-message {
  margin-top: 20px;
  padding: 15px;
  border-radius: 4px;
  text-align: center;
}

.complete-message button {
  margin-top: 10px;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: #6c757d;
  color: white;
  cursor: pointer;
}

.complete-message button:hover {
  background-color: #5a6268;
}

.message {
  padding: 10px;
  border-radius: 4px;
  font-size: 14px;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>