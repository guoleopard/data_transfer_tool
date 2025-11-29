<template>
  <div class="migration-progress">
    <div class="progress-header">
      <h3>迁移进度</h3>
      <el-tag :type="getStatusType(status)">{{ getStatusText(status) }}</el-tag>
    </div>
    
    <div class="progress-bar-container">
      <el-progress 
        :percentage="progress" 
        :status="getProgressStatus(status)"
        :stroke-width="20"
        :text-inside="true"
      />
      <div class="progress-stats">
        <span>已完成: {{ progress }}%</span>
        <span>状态: {{ getStatusText(status) }}</span>
      </div>
    </div>
    
    <div class="progress-logs">
      <div class="logs-header">
        <h4>迁移日志</h4>
        <el-button type="text" size="small" @click="clearLogs" v-if="logs.length > 0">
          <el-icon><Delete /></el-icon>
          清空日志
        </el-button>
      </div>
      
      <div class="logs-container" ref="logsContainer">
        <div 
          v-for="(log, index) in logs" 
          :key="index"
          class="log-item"
          :class="getLogClass(log.type)"
        >
          <span class="log-time">{{ log.time }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
        
        <div v-if="logs.length === 0" class="no-logs">
          <el-empty description="暂无日志信息" :image-size="80" />
        </div>
      </div>
    </div>
    
    <div class="progress-actions" v-if="status === 'completed' || status === 'error'">
      <el-button 
        type="primary" 
        @click="$emit('restart')"
      >
        <el-icon><Refresh /></el-icon>
        重新开始
      </el-button>
      <el-button @click="exportLogs">
        <el-icon><Download /></el-icon>
        导出日志
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete, Refresh, Download } from '@element-plus/icons-vue'

const props = defineProps({
  progress: {
    type: Number,
    default: 0
  },
  status: {
    type: String,
    default: 'pending' // pending, running, completed, error
  },
  logs: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['restart', 'clear-logs'])

const logsContainer = ref()

// 监听日志变化，自动滚动到底部
watch(() => props.logs, () => {
  nextTick(() => {
    if (logsContainer.value) {
      logsContainer.value.scrollTop = logsContainer.value.scrollHeight
    }
  })
}, { deep: true })

const getStatusType = (status) => {
  const typeMap = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    error: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    pending: '等待开始',
    running: '迁移中',
    completed: '迁移完成',
    error: '迁移失败'
  }
  return textMap[status] || '未知状态'
}

const getProgressStatus = (status) => {
  const statusMap = {
    pending: '',
    running: '',
    completed: 'success',
    error: 'exception'
  }
  return statusMap[status] || ''
}

const getLogClass = (type) => {
  return `log-${type || 'info'}`
}

const clearLogs = () => {
  emit('clear-logs')
  ElMessage.success('日志已清空')
}

const exportLogs = () => {
  const logContent = props.logs.map(log => 
    `[${log.time}] ${log.message}`
  ).join('\n')
  
  const blob = new Blob([logContent], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `migration-logs-${new Date().toISOString().slice(0, 10)}.txt`
  link.click()
  
  URL.revokeObjectURL(url)
  ElMessage.success('日志导出成功')
}
</script>

<style scoped>
.migration-progress {
  padding: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.progress-header h3 {
  margin: 0;
  color: #303133;
}

.progress-bar-container {
  margin-bottom: 30px;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-size: 14px;
  color: #909399;
}

.progress-logs {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 20px;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.logs-header h4 {
  margin: 0;
  color: #303133;
}

.logs-container {
  height: 300px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
}

.log-item {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 13px;
  font-family: 'Courier New', monospace;
}

.log-time {
  color: #909399;
  white-space: nowrap;
}

.log-message {
  flex: 1;
  color: #303133;
}

.log-info .log-message {
  color: #409eff;
}

.log-success .log-message {
  color: #67c23a;
}

.log-warning .log-message {
  color: #e6a23c;
}

.log-error .log-message {
  color: #f56c6c;
}

.no-logs {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.progress-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

/* 自定义滚动条 */
.logs-container::-webkit-scrollbar {
  width: 6px;
}

.logs-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.logs-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.logs-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>