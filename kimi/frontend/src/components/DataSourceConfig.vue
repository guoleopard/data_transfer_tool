<template>
  <div class="data-source-config">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>数据源设置</span>
          <el-button type="primary" size="small" @click="testConnection">
            <el-icon><Connection /></el-icon>
            测试连接
          </el-button>
        </div>
      </template>
      
      <el-form :model="formData" label-width="120px" :rules="rules" ref="formRef">
        <el-form-item label="数据库类型" prop="dbType">
          <el-select v-model="formData.dbType" placeholder="请选择数据库类型">
            <el-option label="MySQL" value="mysql" />
            <el-option label="SQL Server" value="sqlserver" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="主机地址" prop="host">
          <el-input v-model="formData.host" placeholder="例如: localhost" />
        </el-form-item>
        
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="formData.port" :min="1" :max="65535" />
        </el-form-item>
        
        <el-form-item label="数据库名" prop="database">
          <el-input v-model="formData.database" placeholder="请输入数据库名称" />
        </el-form-item>
        
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="formData.password" 
            type="password" 
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveConfig">保存配置</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Connection } from '@element-plus/icons-vue'

const props = defineProps({
  configType: {
    type: String,
    default: 'source' // 'source' 或 'target'
  },
  initialConfig: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['save', 'test-connection'])

const formRef = ref()

const formData = reactive({
  dbType: 'mysql',
  host: 'localhost',
  port: 3306,
  database: '',
  username: '',
  password: ''
})

const rules = {
  dbType: [{ required: true, message: '请选择数据库类型', trigger: 'change' }],
  host: [{ required: true, message: '请输入主机地址', trigger: 'blur' }],
  port: [{ required: true, message: '请输入端口', trigger: 'blur' }],
  database: [{ required: true, message: '请输入数据库名', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

// 监听数据库类型变化，自动设置默认端口
watch(() => formData.dbType, (newType) => {
  if (newType === 'mysql') {
    formData.port = 3306
  } else if (newType === 'sqlserver') {
    formData.port = 1433
  }
})

// 初始化配置
if (props.initialConfig && Object.keys(props.initialConfig).length > 0) {
  Object.assign(formData, props.initialConfig)
}

const testConnection = async () => {
  try {
    await formRef.value.validate()
    emit('test-connection', formData)
    ElMessage.success('连接测试已发送')
  } catch (error) {
    ElMessage.error('请检查表单填写是否正确')
  }
}

const saveConfig = async () => {
  try {
    await formRef.value.validate()
    emit('save', {
      type: props.configType,
      config: { ...formData }
    })
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('请检查表单填写是否正确')
  }
}

const resetForm = () => {
  formRef.value.resetFields()
  formData.dbType = 'mysql'
  formData.host = 'localhost'
  formData.port = 3306
}
</script>

<style scoped>
.data-source-config {
  margin-bottom: 20px;
}

.config-card {
  max-width: 600px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>