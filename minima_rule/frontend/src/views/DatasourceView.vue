<template>
  <div class="datasource-view">
    <div class="view-header">
      <h2>数据源管理</h2>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        添加数据源
      </el-button>
    </div>

    <el-card>
      <el-table :data="datasources" border stripe>
        <el-table-column prop="name" label="数据源名称" />
        <el-table-column prop="type" label="数据库类型">
          <template #default="scope">
            <el-tag :type="scope.row.type === 'mysql' ? 'success' : 'primary'">
              {{ scope.row.type === 'mysql' ? 'MySQL' : 'SQL Server' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="host" label="地址" />
        <el-table-column prop="database" label="数据库" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button size="small" @click="editDatasource(scope.row)">
              编辑
            </el-button>
            <el-button size="small" type="success" @click="testConnection(scope.row)">
              测试连接
            </el-button>
            <el-button size="small" type="danger" @click="deleteDatasource(scope.row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑数据源对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingDatasource ? '编辑数据源' : '添加数据源'"
      width="500px"
    >
      <el-form :model="formData" label-width="100px">
        <el-form-item label="数据源名称" required>
          <el-input v-model="formData.name" placeholder="请输入数据源名称" />
        </el-form-item>
        <el-form-item label="数据库类型" required>
          <el-select v-model="formData.type" placeholder="请选择数据库类型">
            <el-option label="MySQL" value="mysql" />
            <el-option label="SQL Server" value="sqlserver" />
          </el-select>
        </el-form-item>
        <el-form-item label="主机地址" required>
          <el-input v-model="formData.host" placeholder="请输入主机地址" />
        </el-form-item>
        <el-form-item label="端口">
          <el-input-number v-model="formData.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="用户名" required>
          <el-input v-model="formData.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" required>
          <el-input v-model="formData.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="数据库名称">
          <el-input v-model="formData.database" placeholder="请输入数据库名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDatasource">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useAppStore } from '../stores/useAppStore'
import { testMysqlConnection, testSqlServerConnection } from '../utils/db'

const store = useAppStore()
const datasources = ref([])
const showAddDialog = ref(false)
const editingDatasource = ref(null)

const formData = ref({
  name: '',
  type: 'mysql',
  host: 'localhost',
  port: 3306,
  username: '',
  password: '',
  database: ''
})

onMounted(() => {
  store.loadDatasources()
  datasources.value = store.datasources
})

const editDatasource = (datasource) => {
  editingDatasource.value = datasource
  formData.value = { ...datasource }
  showAddDialog.value = true
}

const saveDatasource = () => {
  if (!formData.value.name || !formData.value.host || !formData.value.username) {
    ElMessage.error('请填写必填字段')
    return
  }

  if (editingDatasource.value) {
    store.updateDatasource(editingDatasource.value.id, formData.value)
    ElMessage.success('数据源更新成功')
  } else {
    store.addDatasource(formData.value)
    ElMessage.success('数据源添加成功')
  }

  showAddDialog.value = false
  editingDatasource.value = null
  formData.value = {
    name: '',
    type: 'mysql',
    host: 'localhost',
    port: 3306,
    username: '',
    password: '',
    database: ''
  }
}

const deleteDatasource = async (id) => {
  try {
    await ElMessageBox.confirm(
      '此操作将永久删除该数据源, 是否继续?',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    store.deleteDatasource(id)
    ElMessage.success('删除成功!')
  } catch {
    ElMessage.info('已取消删除')
  }
}

const testConnection = async (datasource) => {
  const loading = ElMessage.loading({ message: '正在测试连接...', duration: 0 })
  try {
    let result
    if (datasource.type === 'mysql') {
      result = await testMysqlConnection(datasource)
    } else {
      result = await testSqlServerConnection(datasource)
    }
    
    loading.close()
    if (result.success) {
      ElMessage.success(result.message)
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    loading.close()
    ElMessage.error('连接测试失败: ' + error.message)
  }
}
</script>

<style scoped>
.datasource-view {
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
</style>