<script setup>
import { ref } from 'vue'
import { Operation, Coin, Setting } from '@element-plus/icons-vue'
import MigrationTask from './components/MigrationTask.vue'
import DataSourceManager from './components/DataSourceManager.vue'

const activeTab = ref('datasource')
</script>

<template>
  <div class="app-container">
    <el-container>
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo-section">
            <el-icon class="logo-icon"><Coin /></el-icon>
            <h1>数据库迁移工具</h1>
          </div>
          <div class="header-actions">
            <el-button type="primary" size="small">
              <el-icon><DataLine /></el-icon>
              迁移历史
            </el-button>
          </div>
        </div>
      </el-header>
      
      <el-main class="app-main">
        <el-card class="main-card">
          <el-tabs v-model="activeTab" class="main-tabs">
            <el-tab-pane label="数据源管理" name="datasource">
              <template #label>
                <span>
                  <el-icon><Coin /></el-icon>
                  数据源管理
                </span>
              </template>
              <DataSourceManager />
            </el-tab-pane>
            
            <el-tab-pane label="迁移任务" name="task">
              <template #label>
                <span>
                  <el-icon><Operation /></el-icon>
                  迁移任务
                </span>
              </template>
              <MigrationTask />
            </el-tab-pane>
            
            <el-tab-pane label="系统设置" name="settings">
              <template #label>
                <span>
                  <el-icon><Setting /></el-icon>
                  系统设置
                </span>
              </template>
              <div class="settings-content">
                <el-alert
                  title="系统设置功能开发中..."
                  type="info"
                  :closable="false"
                />
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-main>
      
      <el-footer class="app-footer">
        <div class="footer-content">
          <p>&copy; 2024 数据库迁移工具 - 支持MySQL和SQL Server数据库迁移</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<style scoped>
/* 全页面展示样式 */
.app-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
}

.el-container {
  height: 100vh;
}

.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 0;
  height: 70px !important;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 30px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo-icon {
  font-size: 32px;
  color: #409eff;
}

.logo-section h1 {
  margin: 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.app-main {
  padding: 0;
  overflow: hidden;
  flex: 1;
}

.main-card {
  height: 100%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.main-tabs {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.datasource-content,
.settings-content {
  padding: 40px 20px;
  text-align: center;
  flex: 1;
}

.app-footer {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
  padding: 15px;
  height: 50px !important;
}

.footer-content p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

/* 标签页样式优化 */
:deep(.el-tabs) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

:deep(.el-tabs__content) {
  flex: 1;
}

:deep(.el-tab-pane) {
  height: 100%;
}

:deep(.el-tabs__item) {
  height: 50px;
  line-height: 50px;
  font-size: 15px;
  font-weight: 500;
}

:deep(.el-tabs__item.is-active) {
  color: #409eff;
}

:deep(.el-tabs__active-bar) {
  background-color: #409eff;
  height: 3px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 15px;
  }
  
  .logo-section h1 {
    font-size: 20px;
  }
  
  .app-main {
    padding: 0;
  }
}
</style>
