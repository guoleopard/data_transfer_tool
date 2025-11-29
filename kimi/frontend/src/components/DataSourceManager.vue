<template>
  <div class="datasource-manager">
    <div class="manager-header">
      <h2>数据源管理</h2>
      <el-button type="primary" @click="showAddDialog = true" :icon="Plus">
        添加数据源
      </el-button>
    </div>

    <div class="datasource-list">
      <el-card v-for="ds in dataSources" :key="ds.id" class="datasource-card">
        <template #header>
          <div class="card-header">
            <span class="datasource-name">{{ ds.name }}</span>
            <div class="card-actions">
              <el-button type="primary" text @click="handleTestConnection(ds)" :loading="testingId === ds.id">
                <el-icon><Connection /></el-icon>
                测试
              </el-button>
              <el-button type="warning" text @click="editDataSource(ds)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button type="danger" text @click="deleteDataSource(ds)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>
        </template>
        
        <div class="datasource-info">
          <div class="info-item">
            <el-icon><Coin /></el-icon>
            <span class="info-label">类型：</span>
            <el-tag :type="ds.db_type === 'mysql' ? 'success' : 'primary'" size="small">
              {{ ds.db_type === 'mysql' ? 'MySQL' : 'SQL Server' }}
            </el-tag>
          </div>
          <div class="info-item">
            <el-icon><Location /></el-icon>
            <span class="info-label">主机：</span>
            <span class="info-value">{{ ds.host }}:{{ ds.port }}</span>
          </div>
          <div class="info-item">
            <el-icon><User /></el-icon>
            <span class="info-label">用户名：</span>
            <span class="info-value">{{ ds.username }}</span>
          </div>
          <div class="info-item">
            <el-icon><DataAnalysis /></el-icon>
            <span class="info-label">数据库：</span>
            <span class="info-value">{{ ds.database }}</span>
          </div>
          <div class="info-item">
            <el-icon><Clock /></el-icon>
            <span class="info-label">创建时间：</span>
            <span class="info-value">{{ formatDate(ds.createdAt) }}</span>
          </div>
          <div class="info-item">
            <el-icon><CircleCheck /></el-icon>
            <span class="info-label">状态：</span>
            <el-tag :type="ds.status === 'connected' ? 'success' : 'warning'" size="small">
              {{ getStatusText(ds.status) }}
            </el-tag>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 添加/编辑数据源对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingDataSource ? '编辑数据源' : '添加数据源'"
      width="500px"
      @close="resetForm"
    >
      <el-form :model="formData" :rules="formRules" ref="dataSourceForm" label-width="100px">
        <el-form-item label="数据源名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入数据源名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" placeholder="请输入数据源描述" />
        </el-form-item>
        <el-form-item label="数据库类型" prop="db_type">
          <el-select v-model="formData.db_type" placeholder="请选择数据库类型">
            <el-option label="MySQL" value="mysql" />
            <el-option label="SQL Server" value="sqlserver" />
          </el-select>
        </el-form-item>
        <el-form-item label="主机地址" prop="host">
          <el-input v-model="formData.host" placeholder="请输入主机地址" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="formData.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="formData.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="数据库名" prop="database">
          <el-input v-model="formData.database" placeholder="请输入数据库名" />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="formData.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddDialog = false">取消</el-button>
          <el-button type="primary" @click="saveDataSource" :loading="saving">
            {{ editingDataSource ? '更新' : '保存' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Connection, Edit, Delete, Coin, Location, User, 
  DataAnalysis, Clock, CircleCheck 
} from '@element-plus/icons-vue'
import { testConnection, saveDataSource as saveDataSourceApi, getDataSources } from '@/services/api'

// 数据源列表
const dataSources = ref([])
const testingId = ref(null)
const saving = ref(false)
const showAddDialog = ref(false)
const editingDataSource = ref(null)
const dataSourceForm = ref(null)

// 表单数据
const formData = reactive({
  name: '',
  db_type: 'mysql',
  host: 'localhost',
  port: 3306,
  username: 'root',
  password: '',
  database: '',
  description: '',
  is_active: true
})

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入数据源名称', trigger: 'blur' }],
  db_type: [{ required: true, message: '请选择数据库类型', trigger: 'change' }],
  host: [{ required: true, message: '请输入主机地址', trigger: 'blur' }],
  port: [{ required: true, message: '请输入端口', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  database: [{ required: true, message: '请输入数据库名', trigger: 'blur' }]
}

// 加载数据源列表
const loadDataSources = async () => {
  try {
    const response = await getDataSources()
    dataSources.value = response.data
  } catch (error) {
    ElMessage.error('加载数据源列表失败')
  }
}

// 测试连接
const handleTestConnection = async (dataSource) => {
  testingId.value = dataSource.id
  try {
    const response = await testConnection(dataSource)
    if (response.success) {
      ElMessage.success('连接成功')
      // 更新状态
      const index = dataSources.value.findIndex(ds => ds.id === dataSource.id)
      if (index !== -1) {
        dataSources.value[index].status = 'connected'
      }
    } else {
      ElMessage.error('连接失败：' + response.message)
    }
  } catch (error) {
    ElMessage.error('连接失败')
  } finally {
    testingId.value = null
  }
}

// 保存数据源
const saveDataSource = async () => {
  await dataSourceForm.value.validate(async (valid) => {
    if (!valid) return
    
    saving.value = true
    try {
      const data = {
        ...formData,
        id: editingDataSource.value?.id,
        status: 'unknown',
        createdAt: editingDataSource.value?.createdAt || new Date().toISOString()
      }
      
      const response = await saveDataSourceApi(data)
      if (response.success) {
        ElMessage.success(editingDataSource.value ? '更新成功' : '保存成功')
        showAddDialog.value = false
        loadDataSources()
        resetForm()
      } else {
        ElMessage.error(response.message)
      }
    } catch (error) {
      ElMessage.error('操作失败')
    } finally {
      saving.value = false
    }
  })
}

// 编辑数据源
const editDataSource = (dataSource) => {
  editingDataSource.value = dataSource
  Object.assign(formData, {
    name: dataSource.name,
    db_type: dataSource.db_type,
    host: dataSource.host,
    port: dataSource.port,
    username: dataSource.username,
    password: dataSource.password,
    database: dataSource.database,
    description: dataSource.description || '',
    is_active: dataSource.is_active !== undefined ? dataSource.is_active : true
  })
  showAddDialog.value = true
}

// 删除数据源
const deleteDataSource = async (dataSource) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除数据源 "${dataSource.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 模拟删除操作
    const index = dataSources.value.findIndex(ds => ds.id === dataSource.id)
    if (index !== -1) {
      dataSources.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  } catch (error) {
    // 用户取消删除
  }
}

// 重置表单
const resetForm = () => {
  editingDataSource.value = null
  Object.assign(formData, {
    name: '',
    db_type: 'mysql',
    host: 'localhost',
    port: 3306,
    username: 'root',
    password: '',
    database: '',
    description: '',
    is_active: true
  })
  if (dataSourceForm.value) {
    dataSourceForm.value.clearValidate()
  }
}

// 格式化日期
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'connected': return '已连接'
    case 'unknown': return '未测试'
    default: return '未知'
  }
}

// 初始化
onMounted(() => {
  loadDataSources()
})
</script>

<style scoped>
.datasource-manager {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e4e7ed;
}

.manager-header h2 {
  margin: 0;
  color: #303133;
  font-size: 20px;
  font-weight: 600;
}

.datasource-list {
  flex: 1;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  padding-bottom: 20px;
}

.datasource-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.datasource-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.datasource-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.datasource-info {
  padding: 15px 0;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-label {
  color: #909399;
  min-width: 70px;
}

.info-value {
  color: #606266;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .datasource-manager {
    padding: 15px;
  }
  
  .datasource-list {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .card-actions {
    flex-direction: column;
    gap: 5px;
  }
}
</style>