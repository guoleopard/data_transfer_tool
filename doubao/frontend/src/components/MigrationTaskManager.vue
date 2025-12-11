<template>
  <div class="migration-task-manager">
    <h2>迁移任务管理</h2>
    <el-form :model="migrationTask" label-width="120px" class="form">
      <el-form-item label="任务名称">
        <el-input v-model="migrationTask.name" placeholder="请输入任务名称"></el-input>
      </el-form-item>
      <el-form-item label="源数据源">
        <el-select v-model="migrationTask.source_id" placeholder="请选择源数据源">
          <el-option v-for="source in dataSources" :key="source.id" :label="source.name" :value="source.id"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="目标数据源">
        <el-select v-model="migrationTask.target_id" placeholder="请选择目标数据源">
          <el-option v-for="source in dataSources" :key="source.id" :label="source.name" :value="source.id"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="迁移表名">
        <div v-if="selectedSourceTables.length > 0" class="table-selection">
          <el-checkbox-group v-model="selectedTables">
            <el-checkbox v-for="table in selectedSourceTables" :key="table" :label="table">{{ table }}</el-checkbox>
          </el-checkbox-group>
        </div>
        <div v-else class="no-tables">
          <el-input v-model="migrationTask.table_names" placeholder="请输入表名（逗号分隔）" disabled></el-input>
          <span v-if="migrationTask.source_id" style="color: #909399; font-size: 12px; margin-left: 10px;">请先选择源数据源</span>
        </div>
      </el-form-item>
      <el-form-item label="迁移选项">
        <el-checkbox v-model="migrationTask.migrate_structure">迁移表结构</el-checkbox>
        <el-checkbox v-model="migrationTask.migrate_records">迁移表记录</el-checkbox>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="saveMigrationTask">保存任务</el-button>
      </el-form-item>
    </el-form>
    <el-table :data="migrationTasks" style="width: 100%; margin-top: 20px" border>
      <el-table-column prop="name" label="任务名称"></el-table-column>
      <el-table-column prop="source_id" label="源数据源"></el-table-column>
      <el-table-column prop="target_id" label="目标数据源"></el-table-column>
      <el-table-column prop="status" label="任务状态"></el-table-column>
      <el-table-column prop="progress" label="进度"></el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="startMigrationTask(scope.row)">启动任务</el-button>
          <el-button size="small" type="warning" @click="stopMigrationTask(scope.row)">停止任务</el-button>
          <el-button size="small" type="danger" @click="deleteMigrationTask(scope.row)">删除任务</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { dataSourceApi, migrationTaskApi } from '../utils/api.js';

const migrationTask = reactive({
  name: '',
  source_id: null,
  target_id: null,
  table_names: '',
  migrate_structure: true,
  migrate_records: true
});

const dataSources = ref([]);
const migrationTasks = ref([]);
const selectedSourceTables = ref([]);
const selectedTables = ref([]);

// 加载数据源列表
const loadDataSources = async () => {
  try {
    const response = await dataSourceApi.list();
    dataSources.value = response;
  } catch (error) {
    console.error('加载数据源失败:', error);
    ElMessage.error('加载数据源失败：' + error.message);
  }
};

// 加载源数据源表列表
const loadSourceTables = async (sourceId) => {
  try {
    const response = await dataSourceApi.getTables(sourceId);
    selectedSourceTables.value = response;
    selectedTables.value = [];
  } catch (error) {
    console.error('加载数据源表失败:', error);
    ElMessage.error('加载数据源表失败：' + error.message);
  }
};

// 加载迁移任务列表
const loadMigrationTasks = async () => {
  try {
    const response = await migrationTaskApi.list();
    migrationTasks.value = response;
  } catch (error) {
    console.error('加载迁移任务失败:', error);
    ElMessage.error('加载迁移任务失败：' + error.message);
  }
};

// 监听源数据源变化，加载表列表
watch(() => migrationTask.source_id, (newSourceId) => {
  if (newSourceId) {
    loadSourceTables(newSourceId);
  } else {
    selectedSourceTables.value = [];
    selectedTables.value = [];
  }
});

// 监听选中表变化，更新table_names
watch(selectedTables, (newSelectedTables) => {
  migrationTask.table_names = newSelectedTables.join(',');
}, { deep: true });

// 页面加载时加载数据
onMounted(() => {
  loadDataSources();
  loadMigrationTasks();
});

// 保存迁移任务
const saveMigrationTask = async () => {
  if (!migrationTask.name) {
    ElMessage.warning('请输入任务名称');
    return;
  }
  if (!migrationTask.source_id) {
    ElMessage.warning('请选择源数据源');
    return;
  }
  if (!migrationTask.target_id) {
    ElMessage.warning('请选择目标数据源');
    return;
  }
  if (migrationTask.table_names.trim() === '') {
    ElMessage.warning('请选择或输入要迁移的表名');
    return;
  }
  
  try {
    await migrationTaskApi.create(migrationTask);
    ElMessage.success('迁移任务保存成功！');
    // 重置表单
    Object.assign(migrationTask, {
      name: '',
      source_id: null,
      target_id: null,
      table_names: '',
      migrate_structure: true,
      migrate_records: true
    });
    selectedTables.value = [];
    // 重新加载迁移任务列表
    loadMigrationTasks();
  } catch (error) {
    console.error('保存迁移任务失败:', error);
    ElMessage.error('保存迁移任务失败：' + error.message);
  }
};

// 启动迁移任务
const startMigrationTask = async (row) => {
  try {
    await migrationTaskApi.start(row.id);
    ElMessage.success('迁移任务已启动！');
    // 重新加载迁移任务列表
    loadMigrationTasks();
  } catch (error) {
    console.error('启动迁移任务失败:', error);
    ElMessage.error('启动迁移任务失败：' + error.message);
  }
};

// 停止迁移任务
const stopMigrationTask = async (row) => {
  try {
    await migrationTaskApi.stop(row.id);
    ElMessage.success('迁移任务已停止！');
    // 重新加载迁移任务列表
    loadMigrationTasks();
  } catch (error) {
    console.error('停止迁移任务失败:', error);
    ElMessage.error('停止迁移任务失败：' + error.message);
  }
};

// 删除迁移任务
const deleteMigrationTask = async (row) => {
  try {
    await migrationTaskApi.delete(row.id);
    ElMessage.success('迁移任务删除成功！');
    // 重新加载迁移任务列表
    loadMigrationTasks();
  } catch (error) {
    console.error('删除迁移任务失败:', error);
    ElMessage.error('删除迁移任务失败：' + error.message);
  }
};
</script>

<style scoped>
.migration-task-manager {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.form {
  margin-bottom: 20px;
}

.el-checkbox {
  margin-right: 20px;
  margin-bottom: 10px;
}

.table-selection {
  display: flex;
  flex-wrap: wrap;
  max-height: 200px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.no-tables {
  display: flex;
  align-items: center;
}
</style>