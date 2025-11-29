<template>
  <div id="app">
    <el-container style="min-height: 100vh;">
      <el-header style="background-color: #2f4050; color: white;">
        <h1 style="margin: 0;">数据库迁移工具</h1>
      </el-header>
      <el-container>
        <el-aside width="200px" style="background-color: #33475b;">
          <el-menu
            default-active="1"
            mode="vertical"
            style="background-color: #33475b; color: white; border-right: none;"
          >
            <el-menu-item index="1" @click="activeMenu = 'dataSource'">
              <el-icon><DataAnalysis /></el-icon>
              <span>数据源管理</span>
            </el-menu-item>
            <el-menu-item index="2" @click="activeMenu = 'migration'">
              <el-icon><DataLine /></el-icon>
              <span>迁移任务</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main style="background-color: #f3f3f4;">
          <DataSourceManager v-if="activeMenu === 'dataSource'" />
          <MigrationTask v-if="activeMenu === 'migration'" />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import DataSourceManager from './components/DataSourceManager.vue';
import MigrationTask from './components/MigrationTask.vue';
import { DataAnalysis, DataLine } from '@element-plus/icons-vue';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';

const activeMenu = ref('dataSource');
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  width: 100%;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100%;
  width: 100%;
}
</style>