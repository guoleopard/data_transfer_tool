<template>
  <div class="app-container">
    <el-container>
      <el-header class="app-header">
        <h1>数据库迁移工具</h1>
      </el-header>
      <el-container>
        <el-aside width="200px" class="app-sidebar">
          <el-menu
            :default-active="activeMenu"
            mode="vertical"
            @select="handleMenuSelect"
          >
            <el-menu-item index="datasource">
              <el-icon><Setting /></el-icon>
              <span>数据源管理</span>
            </el-menu-item>
            <el-menu-item index="migration">
              <el-icon><Connection /></el-icon>
              <span>迁移任务</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main class="app-main">
          <component :is="currentView" />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Setting, Connection } from '@element-plus/icons-vue'
import DatasourceView from './views/DatasourceView.vue'
import MigrationView from './views/MigrationView.vue'

const activeMenu = ref('datasource')
const currentView = ref(DatasourceView)

const handleMenuSelect = (key) => {
  activeMenu.value = key
  if (key === 'datasource') {
    currentView.value = DatasourceView
  } else if (key === 'migration') {
    currentView.value = MigrationView
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.app-container {
  width: 100vw;
  height: 100vh;
}

.app-header {
  background: #165DFF;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.app-header h1 {
  font-size: 20px;
  font-weight: 600;
}

.app-sidebar {
  background: #f5f5f5;
}

.app-main {
  padding: 20px;
  background: #fafafa;
}
</style>