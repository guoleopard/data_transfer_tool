<template>
  <div id="app">
    <header class="app-header">
      <h1>数据库迁移工具</h1>
      <p>配置并保存至少两个数据库连接作为源和目标，轻松实现 MySQL 与 SQL Server 之间的数据迁移</p>
    </header>

    <!-- 步骤导航 -->
    <div class="step-nav">
      <div class="step-item" :class="{ active: currentStep === 1, completed: currentStep > 1 }">
        <div class="step-number">1</div>
        <div class="step-title">维护数据源</div>
      </div>
      <div class="step-separator" :class="{ completed: currentStep > 1 }"></div>
      <div class="step-item" :class="{ active: currentStep === 2, completed: currentStep > 2, disabled: !hasSavedDataSources }">
        <div class="step-number">2</div>
        <div class="step-title">创建迁移任务</div>
        <div class="step-desc">选择需要迁移的表，配置迁移类型并保存任务</div>
      </div>
      <div class="step-separator" :class="{ completed: currentStep > 2 }"></div>
      <div class="step-item" :class="{ active: currentStep === 3, completed: currentStep > 3, disabled: !hasMigrationTask }">
        <div class="step-number">3</div>
        <div class="step-title">运行任务</div>
      </div>
    </div>

    <main class="app-main">
      <!-- 步骤1: 维护数据源 -->
      <div v-if="currentStep === 1" class="step-container">
        <div class="config-section">
          <h2>源数据库配置</h2>
          <DataSourceForm @save="handleDataSourceSave('source')" :saved-config="sourceConfig" />
        </div>

        <div class="config-section">
          <h2>目标数据库配置</h2>
          <DataSourceForm @save="handleDataSourceSave('target')" :saved-config="targetConfig" />
        </div>

        <div class="step-controls">
          <button class="btn btn-primary" @click="nextStep" :disabled="!hasSavedDataSources">
            下一步
          </button>
        </div>
      </div>

      <!-- 步骤2: 创建迁移任务 -->
      <div v-else-if="currentStep === 2" class="step-container">
        <div class="migration-section">
          <MigrationTask 
            :source-config="activeSource"
            :target-config="activeTarget"
            @task-created="handleTaskCreated"
          />
        </div>

        <div class="step-controls">
          <button class="btn btn-secondary" @click="prevStep">上一步</button>
          <button class="btn btn-primary" @click="nextStep" :disabled="!hasMigrationTask">
            下一步
          </button>
        </div>
      </div>

      <!-- 步骤3: 运行任务 -->
      <div v-else-if="currentStep === 3" class="step-container">
        <div class="migration-section">
          <MigrationTask 
            :source-config="activeSource"
            :target-config="activeTarget"
            :readonly-all="true"
            :auto-start="true"
            @migration-complete="handleMigrationComplete"
          />
        </div>

        <div class="step-controls">
          <button class="btn btn-secondary" @click="prevStep">上一步</button>
          <button class="btn btn-success" @click="resetWorkflow" v-if="migrationCompleted">
            完成
          </button>
        </div>
      </div>
    </main>

    <footer class="app-footer">
      <p>&copy; 2024 数据库迁移工具</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import DataSourceForm from './components/DataSourceForm.vue'
import MigrationTask from './components/MigrationTask.vue'

const currentStep = ref(1)
const savedDataSources = ref({})
const migrationTask = ref(null)
const migrationCompleted = ref(false)
const activeSource = ref(null)
const activeTarget = ref(null)
const savedMigrationTask = ref(null)
const hasSavedDataSources = ref(false)
const hasMigrationTask = ref(false)

const handleDataSourceSave = (type, config) => {
  savedDataSources.value[config.name || `database-${Object.keys(savedDataSources.value).length + 1}`] = {
    ...config,
    connection: {
      execute: () => Promise.resolve([[{ table_name: 'users' }, { table_name: 'posts' }, { table_name: 'comments' }]]),
      query: () => Promise.resolve({ recordset: [{ TABLE_NAME: 'users' }, { TABLE_NAME: 'posts' }, { TABLE_NAME: 'comments' }] })
    }
  }
  hasSavedDataSources.value = Object.keys(savedDataSources.value).length >= 2
}



const handleMigrationComplete = () => {
  migrationCompleted.value = true
}

const nextStep = () => {
  if (currentStep.value === 1) {
    if (Object.keys(savedDataSources.value).length < 2) {
      alert('请至少保存两个数据源（源数据库和目标数据库）')
      return
    }
    // 自动选择前两个数据源作为源和目标
    const sourceKeys = Object.keys(savedDataSources.value)
    activeSource.value = savedDataSources.value[sourceKeys[0]]
    activeTarget.value = savedDataSources.value[sourceKeys[1]]
    hasSavedDataSources.value = true
  }
  if (currentStep.value === 2 && !hasMigrationTask.value) {
    alert('请先创建并保存迁移任务')
    return
  }
  currentStep.value++
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const resetWorkflow = () => {
  currentStep.value = 1
  migrationTask.value = null
  migrationCompleted.value = false
  hasSavedDataSources.value = false
  hasMigrationTask.value = false
  activeSource.value = null
  activeTarget.value = null
  savedMigrationTask.value = null
}

const handleTaskCreated = (task) => {
  savedMigrationTask.value = task
  hasMigrationTask.value = true
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  color: #333;
}

#app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.app-header {
  text-align: center;
  color: white;
  margin-bottom: 30px;
  padding: 30px 0;
}

.app-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.app-header p {
  font-size: 1.1rem;
  opacity: 0.9;
}

/* 步骤导航 */
.step-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 120px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.step-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.step-item.active .step-number {
  background: #667eea;
  color: white;
  transform: scale(1.2);
}

.step-item.completed .step-number {
  background: #10b981;
  color: white;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  transition: all 0.3s ease;
  background: white;
}

.step-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: #6b7280;
}

.step-item.active .step-title {
  color: #667eea;
  font-weight: 600;
}

.step-item.completed .step-title {
  color: #10b981;
}

.step-separator {
  flex: 1;
  height: 2px;
  background: #e5e7eb;
  margin: 0 20px;
  transition: all 0.3s ease;
}

.step-separator.completed {
  background: #10b981;
}

.app-main {
  margin-bottom: 30px;
}

.step-container {
  display: grid;
  gap: 30px;
}

.config-section, .migration-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.config-section h2, .migration-section h2 {
  color: #667eea;
  margin-bottom: 20px;
  font-size: 1.5rem;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 10px;
}

/* 步骤控制按钮 */
.step-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #4b5563;
  transform: translateY(-2px);
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-2px);
}

.app-footer {
  text-align: center;
  color: white;
  opacity: 0.8;
  padding: 20px 0;
}

@media (max-width: 768px) {
  #app {
    padding: 10px;
  }
  
  .app-header h1 {
    font-size: 2rem;
  }
  
  .step-nav {
    flex-wrap: wrap;
    gap: 20px;
  }
  
  .step-separator {
    display: none;
  }
  
  .step-container {
    gap: 20px;
  }
  
  .step-controls {
    flex-direction: column;
  }
}
</style>