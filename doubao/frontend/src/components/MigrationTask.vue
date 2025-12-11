<template>
  <div class="migration-task">
    <h2>迁移任务管理</h2>
    <el-form :model="migrationTask" label-width="100px" class="form">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="源数据源">
            <el-select v-model="migrationTask.sourceId" placeholder="请选择源数据源">
              <el-option
                v-for="source in dataSources"
                :key="source.name"
                :label="source.name"
                :value="source.name"
              ></el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="目标数据源">
            <el-select v-model="migrationTask.targetId" placeholder="请选择目标数据源">
              <el-option
                v-for="target in dataSources"
                :key="target.name"
                :label="target.name"
                :value="target.name"
              ></el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="迁移类型">
        <el-checkbox-group v-model="migrationTask.migrationType">
          <el-checkbox label="结构迁移"></el-checkbox>
          <el-checkbox label="数据迁移"></el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="选择表">
        <el-button type="primary" @click="loadTables">加载表结构</el-button>
        <el-tree
          :data="tableTree"
          show-checkbox
          node-key="name"
          ref="tableTreeRef"
          :props="{ label: 'name', children: 'columns' }"
          style="margin-top: 10px"
        ></el-tree>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="startMigration">开始迁移</el-button>
        <el-button @click="resetTask">重置任务</el-button>
      </el-form-item>
    </el-form>
    <el-table :data="migrationHistory" style="width: 100%; margin-top: 20px" border>
      <el-table-column prop="name" label="任务名称"></el-table-column>
      <el-table-column prop="source" label="源数据源"></el-table-column>
      <el-table-column prop="target" label="目标数据源"></el-table-column>
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag :type="scope.row.status === 'completed' ? 'success' : scope.row.status === 'running' ? 'warning' : 'info'">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="progress" label="进度">
        <template #default="scope">
          <el-progress :percentage="scope.row.progress" v-if="scope.row.status === 'running' || scope.row.status === 'completed'"></el-progress>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="createTime" label="创建时间"></el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="viewLog(scope.row)">查看日志</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { dataSourceApi, migrationTaskApi } from '../api/api';

const migrationTask = reactive({
  name: '',
  sourceId: '',
  targetId: '',
  migrationType: [],
  tables: []
});

const dataSources = ref([]);

const tableTree = ref([]);
const tableTreeRef = ref();
const migrationHistory = ref([]);

const loadTables = async () => {
  if (!migrationTask.sourceId) {
    ElMessage.warning('请先选择源数据源');
    return;
  }
  const source = dataSources.value.find(ds => ds.name === migrationTask.sourceId);
  if (!source) {
    ElMessage.warning('源数据源不存在');
    return;
  }
  
  try {
    // 调用后端API加载表结构
    const response = await dataSourceApi.getDataSourceTables(source.id);
    tableTree.value = response.tables;
    ElMessage.success('表结构加载成功！');
  } catch (error) {
    console.error('加载表结构失败:', error);
    ElMessage.error('加载表结构失败：' + error.message);
  }
};

const startMigration = async () => {
  if (!migrationTask.sourceId || !migrationTask.targetId) {
    ElMessage.warning('请选择源数据源和目标数据源');
    return;
  }
  if (migrationTask.migrationType.length === 0) {
    ElMessage.warning('请选择迁移类型');
    return;
  }
  const checkedKeys = tableTreeRef.value.getCheckedKeys();
  if (checkedKeys.length === 0) {
    ElMessage.warning('请选择需要迁移的表');
    return;
  }
  
  try {
    // 调用后端API创建迁移任务
    const taskData = {
      name: `迁移任务_${Date.now()}`,
      source_id: dataSources.value.find(ds => ds.name === migrationTask.sourceId).id,
      target_id: dataSources.value.find(ds => ds.name === migrationTask.targetId).id,
      table_names: checkedKeys.join(','),
      migrate_structure: migrationTask.migrationType.includes('结构迁移'),
      migrate_records: migrationTask.migrationType.includes('数据迁移')
    };
    const response = await migrationTaskApi.createMigrationTask(taskData);
    migrationHistory.value.push(response);
    ElMessage.success('迁移任务已启动！');
    
    // 开始迁移
    await migrationTaskApi.startMigration(response.id);
  } catch (error) {
    console.error('启动迁移任务失败:', error);
    ElMessage.error('启动迁移任务失败：' + error.message);
  }
};

// 监听迁移进度
const watchMigrationProgress = async (task) => {
  try {
    while (task.status === 'running') {
      const response = await migrationTaskApi.getMigrationProgress(task.id);
      task.progress = response.progress;
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    // 获取最终的迁移日志
    const logResponse = await migrationTaskApi.getMigrationLog(task.id);
    task.log = logResponse.log;
    ElMessage.success('迁移任务已完成！');
  } catch (error) {
    console.error('获取迁移进度失败:', error);
    ElMessage.error('获取迁移进度失败：' + error.message);
  }
};

const resetTask = () => {
  Object.assign(migrationTask, {
    name: '',
    sourceId: '',
    targetId: '',
    migrationType: [],
    tables: []
  });
  tableTree.value = [];
  if (tableTreeRef.value) {
    tableTreeRef.value.setCheckedKeys([]);
  }
};

const viewLog = async (task) => {
  try {
    // 调用后端API获取迁移日志
    const response = await migrationTaskApi.getMigrationLog(task.id);
    ElMessageBox.alert(
      `<pre>${response.log.join('\n')}</pre>`,
      `任务日志 - ${task.name}`,
      {
        dangerouslyUseHTMLString: true,
        showClose: true,
        confirmButtonText: '关闭'
      }
    );
  } catch (error) {
    console.error('获取迁移日志失败:', error);
    ElMessage.error('获取迁移日志失败：' + error.message);
  }
};

// 加载数据源列表
const loadDataSources = async () => {
  try {
    const response = await dataSourceApi.getDataSources();
    dataSources.value = response;
  } catch (error) {
    console.error('加载数据源列表失败:', error);
    ElMessage.error('加载数据源列表失败：' + error.message);
  }
};

// 加载迁移任务列表
const loadMigrationTasks = async () => {
  try {
    const response = await migrationTaskApi.getMigrationTasks();
    migrationHistory.value = response;
  } catch (error) {
    console.error('加载迁移任务列表失败:', error);
    ElMessage.error('加载迁移任务列表失败：' + error.message);
  }
};

// 组件挂载时加载数据源列表和迁移任务列表
onMounted(() => {
  loadDataSources();
  loadMigrationTasks();
});
</script>

<style scoped>
.migration-task {
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

.el-tree {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
  max-height: 300px;
  overflow-y: auto;
}
</style>