<template>
  <div class="migration-view">
    <div class="view-header">
      <h2>迁移任务</h2>
    </div>

    <el-card>
      <el-form :model="formData" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="源数据库" required>
              <el-select v-model="formData.sourceId" placeholder="请选择源数据库" @change="handleSourceChange">
                <el-option
                  v-for="ds in datasources"
                  :key="ds.id"
                  :label="`${ds.name} (${ds.type === 'mysql' ? 'MySQL' : 'SQL Server'})`"
                  :value="ds.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标数据库" required>
              <el-select v-model="formData.targetId" placeholder="请选择目标数据库" @change="handleTargetChange">
                <el-option
                  v-for="ds in datasources"
                  :key="ds.id"
                  :label="`${ds.name} (${ds.type === 'mysql' ? 'MySQL' : 'SQL Server'})`"
                  :value="ds.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="迁移类型" required>
          <el-checkbox-group v-model="formData.migrationType">
            <el-checkbox label="structure">结构迁移</el-checkbox>
            <el-checkbox label="data">数据迁移</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="选择数据表" required>
          <div v-if="sourceTables.length > 0">
            <el-checkbox-group v-model="formData.selectedTables">
              <el-checkbox
                v-for="table in sourceTables"
                :key="table"
                :label="table"
              />
            </el-checkbox-group>
          </div>
          <div v-else style="color: #909399;">
            请先选择源数据库加载数据表
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="migrationRunning"
            :disabled="!canStartMigration"
            @click="startMigration"
          >
            开始迁移
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 迁移进度 -->
    <el-card v-if="showProgress" title="迁移进度">
      <div v-for="(progress, tableName) in migrationProgress" :key="tableName" class="progress-item">
        <div class="progress-header">
          <span>{{ tableName }}</span>
          <span>{{ progress.percentage }}%</span>
        </div>
        <el-progress :percentage="progress.percentage" :status="progress.status" />
        <div class="progress-info">{{ progress.message }}</div>
      </div>

      <div class="total-progress" v-if="Object.keys(migrationProgress).length > 0">
        <div class="progress-header">
          <span>总体进度</span>
          <span>{{ totalProgress }}%</span>
        </div>
        <el-progress :percentage="totalProgress" :status="totalStatus" stripe />
      </div>

      <div class="migration-result" v-if="migrationCompleted">
        <el-alert
          :title="migrationSuccess ? '迁移完成！' : '迁移失败！'"
          :type="migrationSuccess ? 'success' : 'error'"
          show-icon
        />
        <div class="result-details">
          <p>成功迁移 {{ successCount }} 张表，失败 {{ failCount }} 张表</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAppStore } from '../stores/useAppStore'
import { getMysqlTables, getSqlServerTables, getMysqlTableSchema, createTable, migrateTableData } from '../utils/db'

const store = useAppStore()
const datasources = ref([])

const formData = ref({
  sourceId: '',
  targetId: '',
  migrationType: [],
  selectedTables: []
})

const sourceTables = ref([])
const migrationRunning = ref(false)
const showProgress = ref(false)
const migrationProgress = ref({})
const totalProgress = ref(0)
const totalStatus = ref('')
const migrationCompleted = ref(false)
const migrationSuccess = ref(false)
const successCount = ref(0)
const failCount = ref(0)

onMounted(() => {
  store.loadDatasources()
  datasources.value = store.datasources
})

const canStartMigration = computed(() => {
  return formData.value.sourceId &&
    formData.value.targetId &&
    formData.value.sourceId !== formData.value.targetId &&
    formData.value.migrationType.length > 0 &&
    formData.value.selectedTables.length > 0
})

const getDatasourceById = (id) => {
  return datasources.value.find(ds => ds.id === id)
}

const handleSourceChange = async (id) => {
  if (!id) return
  
  const datasource = getDatasourceById(id)
  if (!datasource) return

  const loading = ElMessage.loading({ message: '正在加载数据表...', duration: 0 })
  try {
    let tables
    if (datasource.type === 'mysql') {
      tables = await getMysqlTables(datasource)
    } else {
      tables = await getSqlServerTables(datasource)
    }
    sourceTables.value = tables
    formData.value.selectedTables = tables
    loading.close()
  } catch (error) {
    loading.close()
    ElMessage.error('加载数据表失败: ' + error.message)
  }
}

const handleTargetChange = (id) => {
  // 可以在这里添加目标数据库验证
}

const startMigration = async () => {
  try {
    let migrationDesc = ''
    if (formData.value.migrationType.includes('structure') && formData.value.migrationType.includes('data')) {
      migrationDesc = '结构和数据'
    } else if (formData.value.migrationType.includes('structure')) {
      migrationDesc = '结构'
    } else if (formData.value.migrationType.includes('data')) {
      migrationDesc = '数据'
    }
    
    await ElMessageBox.confirm(
      `确认开始迁移？将迁移 ${formData.value.selectedTables.length} 张表的${migrationDesc}。`,
      '确认迁移',
      {
        confirmButtonText: '开始迁移',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    migrationRunning.value = true
    showProgress.value = true
    migrationCompleted.value = false
    migrationSuccess.value = false
    successCount.value = 0
    failCount.value = 0
    migrationProgress.value = {}
    totalProgress.value = 0

    const sourceDs = getDatasourceById(formData.value.sourceId)
    const targetDs = getDatasourceById(formData.value.targetId)
    const totalTables = formData.value.selectedTables.length
    let completedTables = 0

    for (const tableName of formData.value.selectedTables) {
      migrationProgress.value[tableName] = {
        percentage: 0,
        message: '准备迁移',
        status: 'active'
      }

      try {
        // 结构迁移
        if (formData.value.migrationType.includes('structure')) {
          migrationProgress.value[tableName].message = '正在迁移表结构'
          let schema
          if (sourceDs.type === 'mysql') {
            schema = await getMysqlTableSchema(sourceDs, tableName)
          }
          await createTable(targetDs, tableName, schema, targetDs.type)
        }

        // 数据迁移
        if (formData.value.migrationType.includes('data')) {
          migrationProgress.value[tableName].message = '正在迁移表数据'
          await migrateTableData(sourceDs, targetDs, tableName, sourceDs.type, targetDs.type, (percentage, message) => {
            migrationProgress.value[tableName].percentage = percentage
            migrationProgress.value[tableName].message = message
          })
        }

        migrationProgress.value[tableName].percentage = 100
        migrationProgress.value[tableName].message = '迁移完成'
        migrationProgress.value[tableName].status = 'success'
        successCount.value++
      } catch (error) {
        migrationProgress.value[tableName].message = '迁移失败: ' + error.message
        migrationProgress.value[tableName].status = 'exception'
        failCount.value++
      }

      completedTables++
      totalProgress.value = Math.round((completedTables / totalTables) * 100)
    }

    migrationCompleted.value = true
    migrationSuccess.value = failCount.value === 0
    totalStatus.value = migrationSuccess.value ? 'success' : 'exception'
    migrationRunning.value = false

    if (migrationSuccess.value) {
      ElMessage.success('所有表迁移完成！')
    } else {
      ElMessage.warning(`迁移完成，但有 ${failCount.value} 张表迁移失败`)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('迁移失败: ' + error.message)
      migrationRunning.value = false
    }
  }
}
</script>

<style scoped>
.migration-view {
  width: 100%;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.view-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.progress-item {
  margin-bottom: 24px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.progress-info {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.total-progress {
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.migration-result {
  margin-top: 20px;
}

.result-details {
  margin-top: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}
</style>