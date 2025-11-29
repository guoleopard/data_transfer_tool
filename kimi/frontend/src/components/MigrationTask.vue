<template>
  <div class="migration-task">
    <el-card class="task-card">
      <template #header>
        <div class="card-header">
          <span>迁移任务设置</span>
          <el-tag :type="taskStatus.type">{{ taskStatus.text }}</el-tag>
        </div>
      </template>
      
      <el-steps :active="currentStep" finish-status="success" class="task-steps">
        <el-step title="选择数据源" />
        <el-step title="选择表" />
        <el-step title="设置迁移类型" />
        <el-step title="执行迁移" />
      </el-steps>
      
      <!-- 步骤1: 选择数据源 -->
      <div v-if="currentStep === 0" class="step-content">
        <el-alert
          title="请选择数据来源和目标数据库"
          type="info"
          :closable="false"
          class="step-alert"
        />
        
        <div class="database-selection">
          <div class="db-section">
            <h3>来源数据库</h3>
            <el-select 
              v-model="selectedSource" 
              placeholder="选择来源数据库"
              style="width: 100%"
            >
              <el-option
                v-for="db in availableDatabases"
                :key="db.id"
                :label="db.name"
                :value="db.id"
              >
                <div class="db-option">
                  <el-icon><Coin /></el-icon>
                  <span>{{ db.name }}</span>
                  <el-tag size="small">{{ db.type }}</el-tag>
                </div>
              </el-option>
            </el-select>
            <el-button 
              type="primary" 
              size="small" 
              @click="showSourceConfig = true"
              class="config-btn"
            >
              <el-icon><Plus /></el-icon>
              添加数据源
            </el-button>
          </div>
          
          <div class="db-section">
            <h3>目标数据库</h3>
            <el-select 
              v-model="selectedTarget" 
              placeholder="选择目标数据库"
              style="width: 100%"
            >
              <el-option
                v-for="db in availableDatabases"
                :key="db.id"
                :label="db.name"
                :value="db.id"
              >
                <div class="db-option">
                  <el-icon><Coin /></el-icon>
                  <span>{{ db.name }}</span>
                  <el-tag size="small">{{ db.type }}</el-tag>
                </div>
              </el-option>
            </el-select>
            <el-button 
              type="primary" 
              size="small" 
              @click="showTargetConfig = true"
              class="config-btn"
            >
              <el-icon><Plus /></el-icon>
              添加数据源
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 步骤2: 选择表 -->
      <div v-if="currentStep === 1" class="step-content">
        <el-alert
          title="选择需要迁移的表"
          type="info"
          :closable="false"
          class="step-alert"
        />
        
        <div class="table-selection">
          <div class="table-header">
            <el-input
              v-model="tableSearch"
              placeholder="搜索表名"
              style="width: 300px"
              clearable
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <div class="table-actions">
              <el-button size="small" @click="selectAllTables">全选</el-button>
              <el-button size="small" @click="clearTableSelection">清空</el-button>
            </div>
          </div>
          
          <el-table
            :data="filteredTables"
            style="width: 100%"
            @selection-change="handleTableSelectionChange"
            ref="tableRef"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="name" label="表名" />
            <el-table-column prop="rows" label="行数" width="100" />
            <el-table-column prop="size" label="大小" width="120" />
            <el-table-column prop="comment" label="描述" />
          </el-table>
        </div>
      </div>
      
      <!-- 步骤3: 设置迁移类型 -->
      <div v-if="currentStep === 2" class="step-content">
        <el-alert
          title="选择迁移类型"
          type="info"
          :closable="false"
          class="step-alert"
        />
        
        <div class="migration-type">
          <el-radio-group v-model="migrationType" class="type-radio-group">
            <el-radio label="structure" border>
              <div class="radio-content">
                <el-icon><Document /></el-icon>
                <div class="radio-text">
                  <div class="radio-title">结构迁移</div>
                  <div class="radio-desc">仅迁移表结构，不包含数据</div>
                </div>
              </div>
            </el-radio>
            <el-radio label="data" border>
              <div class="radio-content">
                <el-icon><DataAnalysis /></el-icon>
                <div class="radio-text">
                  <div class="radio-title">数据迁移</div>
                  <div class="radio-desc">迁移表结构和所有数据</div>
                </div>
              </div>
            </el-radio>
            <el-radio label="both" border>
              <div class="radio-content">
                <el-icon><CopyDocument /></el-icon>
                <div class="radio-text">
                  <div class="radio-title">结构和数据</div>
                  <div class="radio-desc">同时迁移表结构和数据</div>
                </div>
              </div>
            </el-radio>
          </el-radio-group>
        </div>
      </div>
      
      <!-- 步骤4: 执行迁移 -->
      <div v-if="currentStep === 3" class="step-content">
        <MigrationProgress 
          :progress="migrationProgress"
          :status="migrationStatus"
          :logs="migrationLogs"
        />
      </div>
      
      <div class="step-actions">
        <el-button v-if="currentStep > 0" @click="prevStep">上一步</el-button>
        <el-button 
          v-if="currentStep < 3" 
          type="primary" 
          @click="nextStep"
          :disabled="!canProceed"
        >
          下一步
        </el-button>
        <el-button 
          v-if="currentStep === 3" 
          type="primary" 
          @click="startMigration"
          :loading="isMigrating"
          :disabled="migrationStatus === 'running'"
        >
          {{ migrationStatus === 'completed' ? '重新迁移' : '开始迁移' }}
        </el-button>
      </div>
    </el-card>
    
    <!-- 数据源配置对话框 -->
    <el-dialog
      v-model="showSourceConfig"
      title="配置来源数据库"
      width="600px"
    >
      <DataSourceConfig 
        config-type="source"
        @save="handleSourceSave"
        @test-connection="handleTestConnection"
      />
    </el-dialog>
    
    <el-dialog
      v-model="showTargetConfig"
      title="配置目标数据库"
      width="600px"
    >
      <DataSourceConfig 
        config-type="target"
        @save="handleTargetSave"
        @test-connection="handleTestConnection"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Coin, Plus, Search, Document, DataAnalysis, CopyDocument } from '@element-plus/icons-vue'
import { getTables, executeMigration } from '@/services/api'
import DataSourceConfig from './DataSourceConfig.vue'
import MigrationProgress from './MigrationProgress.vue'
import { useDataSourceStore } from '@/stores/dataSource'

// 步骤控制
const currentStep = ref(0)
const canProceed = computed(() => {
  switch (currentStep.value) {
    case 0:
      return selectedSource.value && selectedTarget.value
    case 1:
      return selectedTables.value.length > 0
    case 2:
      return migrationType.value !== ''
    default:
      return true
  }
})

// 使用数据源store
const dataSourceStore = useDataSourceStore()

// 数据库选择
const selectedSource = ref('')
const selectedTarget = ref('')
const showSourceConfig = ref(false)
const showTargetConfig = ref(false)

// 表选择
const tableSearch = ref('')
const selectedTables = ref([])
const tableRef = ref()

// 迁移类型
const migrationType = ref('both')

// 迁移状态
const isMigrating = ref(false)
const migrationProgress = ref(0)
const migrationStatus = ref('pending') // pending, running, completed, error
const migrationLogs = ref([])

// 使用 store 中的数据源
const availableDatabases = computed(() => dataSourceStore.getAvailableDataSources)

// 模拟表数据
const availableTables = ref([
  { name: 'users', rows: 1523, size: '2.5MB', comment: '用户表' },
  { name: 'orders', rows: 8456, size: '15.2MB', comment: '订单表' },
  { name: 'products', rows: 234, size: '1.8MB', comment: '产品表' },
  { name: 'categories', rows: 45, size: '256KB', comment: '分类表' },
  { name: 'addresses', rows: 3421, size: '8.3MB', comment: '地址表' },
  { name: 'payments', rows: 6789, size: '12.1MB', comment: '支付记录表' }
])

const filteredTables = computed(() => {
  if (!tableSearch.value) return availableTables.value
  return availableTables.value.filter(table => 
    table.name.toLowerCase().includes(tableSearch.value.toLowerCase())
  )
})

const taskStatus = computed(() => {
  switch (migrationStatus.value) {
    case 'running':
      return { type: 'warning', text: '迁移中' }
    case 'completed':
      return { type: 'success', text: '已完成' }
    case 'error':
      return { type: 'danger', text: '迁移失败' }
    default:
      return { type: 'info', text: '待开始' }
  }
})

// 方法
const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const handleTableSelectionChange = (selection) => {
  selectedTables.value = selection
}

const selectAllTables = () => {
  tableRef.value.toggleAllSelection()
}

const clearTableSelection = () => {
  tableRef.value.clearSelection()
}

const handleSourceSave = (config) => {
  // 通过 store 添加新的数据源
  dataSourceStore.addDataSource({
    id: `db-${Date.now()}`,
    name: `${config.config.dbType}-${config.config.host}`,
    type: config.config.dbType,
    ...config.config
  })
  showSourceConfig.value = false
  ElMessage.success('数据源添加成功')
}

const handleTargetSave = (config) => {
  // 通过 store 添加新的数据源
  dataSourceStore.addDataSource({
    id: `db-${Date.now()}`,
    name: `${config.config.dbType}-${config.config.host}`,
    type: config.config.dbType,
    ...config.config
  })
  showTargetConfig.value = false
  ElMessage.success('数据源添加成功')
}

const handleTestConnection = (config) => {
  // 模拟连接测试
  setTimeout(() => {
    ElMessage.success('连接测试成功')
  }, 1000)
}

const startMigration = async () => {
  if (selectedTables.value.length === 0) {
    ElMessage.warning('请至少选择一个表')
    return
  }
  
  isMigrating.value = true
  migrationStatus.value = 'running'
  migrationProgress.value = 0
  migrationLogs.value = []
  
  try {
    const response = await executeMigration({
      source: selectedSource.value,
      target: selectedTarget.value,
      tables: selectedTables.value,
      migrationType: migrationType.value
    })
    
    if (response.success) {
      migrationStatus.value = 'completed'
      migrationLogs.value = response.logs || []
      ElMessage.success('迁移任务执行成功！')
    } else {
      migrationStatus.value = 'error'
      migrationLogs.value = response.logs || []
      ElMessage.error('迁移任务执行失败')
    }
  } catch (error) {
    migrationStatus.value = 'error'
    migrationLogs.value = ['迁移过程中发生错误']
    ElMessage.error('迁移任务执行失败')
  } finally {
    isMigrating.value = false
  }
}

// 初始化加载数据源
onMounted(() => {
  // 如果store中没有数据源，可以在这里加载默认数据源
  if (dataSourceStore.dataSources.length === 0) {
    // 可以在这里调用API加载默认数据源
  }
})
</script>

<style scoped>
.migration-task {
  max-width: 1000px;
  margin: 0 auto;
}

.task-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-steps {
  margin-bottom: 30px;
}

.step-content {
  min-height: 400px;
}

.step-alert {
  margin-bottom: 20px;
}

.database-selection {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-top: 20px;
}

.db-section {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.db-section h3 {
  margin: 0 0 15px 0;
  color: #303133;
}

.db-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-btn {
  margin-top: 10px;
  width: 100%;
}

.table-selection {
  background: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.migration-type {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

.type-radio-group {
  display: flex;
  gap: 20px;
}

.radio-content {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
}

.radio-text {
  display: flex;
  flex-direction: column;
}

.radio-title {
  font-weight: bold;
  margin-bottom: 4px;
}

.radio-desc {
  font-size: 12px;
  color: #909399;
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}
</style>