<template>
  <div class="data-source-form">
    <h3>{{ title }}</h3>
    <div class="form-group">
        <label>数据源名称</label>
        <input type="text" v-model="form.name" placeholder="输入数据源名称" :disabled="props.readonly" required />
      </div>
      <div class="form-group">
        <label>数据库类型</label>
        <select v-model="form.type" :disabled="props.readonly">
          <option value="mysql">MySQL</option>
          <option value="mssql">SQL Server</option>
        </select>
      </div>
    <div class="form-group">
      <label>主机地址</label>
      <input v-model="form.host" type="text" placeholder="localhost" :disabled="props.readonly" />
    </div>
    <div class="form-group">
      <label>端口</label>
      <input v-model.number="form.port" type="number" :placeholder="form.type === 'mysql' ? 3306 : 1433" :disabled="props.readonly" />
    </div>
    <div class="form-group">
      <label>用户名</label>
      <input v-model="form.username" type="text" placeholder="root" :disabled="props.readonly" />
    </div>
    <div class="form-group">
      <label>密码</label>
      <input v-model="form.password" type="password" :disabled="props.readonly" />
    </div>
    <div class="form-group">
      <label>数据库名</label>
      <input v-model="form.database" type="text" :disabled="props.readonly" />
    </div>
    <div class="button-group" v-if="!props.readonly">
      <button @click="testConnection" :disabled="connecting">
        {{ connecting ? '测试连接中...' : '测试连接' }}
      </button>
      <button @click="saveConnection" :disabled="!connected">保存配置</button>
    </div>
    <div v-if="message" :class="['message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits, defineProps } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: '数据源配置'
  },
  savedConfig: Object,
  readonly: { 
    type: Boolean, 
    default: false 
  }
})

const emit = defineEmits(['save'])

const form = ref({
  name: '',
  type: 'mysql',
  host: 'localhost',
  port: 3306,
  username: 'root',
  password: '',
  database: ''
})

// 初始化已保存配置
if (props.savedConfig) {
  form.value.name = props.savedConfig.name
  form.value.type = props.savedConfig.type
  form.value.host = props.savedConfig.host
  form.value.port = props.savedConfig.port
  form.value.username = props.savedConfig.username
  form.value.password = props.savedConfig.password
  form.value.database = props.savedConfig.database
}

const connecting = ref(false)
const connected = ref(false)
const message = ref(null)
const connection = ref(null)

// 监听数据库类型变化，自动切换默认端口
import { watch } from 'vue'
watch(() => form.value.type, (newType) => {
  form.value.port = newType === 'mysql' ? 3306 : 1433
})

const testConnection = async () => {
  connecting.value = true
  message.value = null
  connected.value = false
  try {
    // 模拟连接成功
    await new Promise(resolve => setTimeout(resolve, 1000))
    connection.value = { connection: {} }
    connected.value = true
    message.value = { type: 'success', text: '连接成功!' }
  } catch (error) {
    message.value = { type: 'error', text: error.message }
  } finally {
    connecting.value = false
  }
}

const saveConnection = () => {
  if (connected.value) {
    emit('save', {
      ...form.value,
      connection: connection.value
    })
    message.value = { type: 'success', text: '配置已保存' }
  }
}
</script>

<style scoped>
.data-source-form {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  background: #fff;
}

.data-source-form h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #333;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #555;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background-color 0.2s;
}

button:not(:disabled) {
  background-color: #42b983;
  color: white;
}

button:not(:disabled):hover {
  background-color: #359469;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
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