<template>
  <div class="migration-task">
    <h2>迁移任务管理</h2>
    <el-form :model="migrationTask" label-width="100px" class="form">
      <el-form-item label="任务名称">
        <el-input v-model="migrationTask.name" placeholder="请输入任务名称"></el-input>
      </el-form-item>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="源数据源">
            <el-select v-model="migrationTask.sourceId" placeholder="请选择源数据源">
              <el-option
                v-for="source in dataSources"
                :key="source.id"
                :label="source.name"
                :value="source.id"
              ></el-option>
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="目标数据源">
            <el-select v-model="migrationTask.targetId" placeholder="请选择目标数据源">
              <el-option
                v-for="target in dataSources"
                :key="target.id"
                :label="target.name"
                :value="target.id"
              ></el-option>
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="迁移类型">
        <el-checkbox v-model="migrationTask.migrate_structure">结构迁移</el-checkbox>
        <el-checkbox v-model="migrationTask.migrate_records">数据迁移</el-checkbox>
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
        <el-button type="primary" @click="saveMigrationTask">
          {{ currentEditingTask ? '更新任务' : '创建任务' }}
        </el-button>
        <el-button @click="resetTask">重置任务</el-button>
      </el-form-item>
    </el-form>
    <el-table :data="migrationHistory" style="width: 100%; margin-top: 20px" border>
      <el-table-column prop="name" label="任务名称"></el-table-column>
      <el-table-column prop="source_id" label="源数据源">
        <template #default="scope">
          {{ dataSources.find(ds => ds.id === scope.row.source_id)?.name || '未知' }}
        </template>
      </el-table-column>
      <el-table-column prop="target_id" label="目标数据源">
        <template #default="scope">
          {{ dataSources.find(ds => ds.id === scope.row.target_id)?.name || '未知' }}
        </template>
      </el-table-column>
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
      <el-table-column prop="create_time" label="创建时间">
        <template #default="scope">
          {{ new Date(scope.row.create_time).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="editTask(scope.row)">编辑</el-button>
          <el-button size="small" type="primary" @click="startMigration(scope.row)" :disabled="scope.row.status !== 'pending'">
            开始迁移
          </el-button>
          <el-button size="small" type="danger" @click="stopMigration(scope.row)" :disabled="scope.row.status !== 'running'">
            停止迁移
          </el-button>
          <el-button size="small" @click="viewLog(scope.row)">查看日志</el-button>
          <el-button size="small" type="danger" @click="deleteTask(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getDataSourceList, createMigrationTask, getMigrationTaskList, getMigrationTaskById, startMigrationTask, stopMigrationTask } from '../api';

const migrationTask = reactive({
  id: null,
  name: '',
  sourceId: null,
  targetId: null,
  migrate_structure: true,
  migrate_records: true,
  table_names: ''
});

const dataSources = ref([]);
const tableTree = ref([]);
const tableTreeRef = ref();
const migrationHistory = ref([]);
const currentEditingTask = ref(null);

// 加载数据源列表
const loadDataSourceList = async () => {
  try {
    const response = await getDataSourceList();
    dataSources.value = response.data;
  } catch (error) {
    console.error('加载数据源列表失败:', error);
    ElMessage.error('加载数据源列表失败：' + error.message);
  }
};

// 加载迁移任务列表
const loadMigrationTaskList = async () => {
  try {
    const response = await getMigrationTaskList();
    migrationHistory.value = response.data;
  } catch (error) {
    console.error('加载迁移任务列表失败:', error);
    ElMessage.error('加载迁移任务列表失败：' + error.message);
  }
};

// 加载表结构 - 暂时使用模拟实现
const loadTables = async () => {
  if (!migrationTask.sourceId) {
    ElMessage.warning('请先选择源数据源');
    return;
  }
  
  try {
    // Mock table data for both MySQL and SQL Server
    const mockTables = [
      { name: 'users', columns: [{ name: 'id' }, { name: 'name' }, { name: 'email' }] },
      { name: 'products', columns: [{ name: 'id' }, { name: 'name' }, { name: 'price' }, { name: 'stock' }] },
      { name: 'orders', columns: [{ name: 'id' }, { name: 'user_id' }, { name: 'product_id' }, { name: 'quantity' }, { name: 'total_amount' }, { name: 'order_date' }] }
    ];
    
    tableTree.value = mockTables;
    ElMessage.success('表结构加载成功！');
  } catch (error) {
    console.error('加载表结构失败:', error);
    ElMessage.error('加载表结构失败：' + error.message);
  }
};

// 保存迁移任务
const saveMigrationTask = async () => {
  if (!migrationTask.name) {
    ElMessage.warning('请输入任务名称');
    return;
  }
  if (!migrationTask.sourceId || !migrationTask.targetId) {
    ElMessage.warning('请选择源数据源和目标数据源');
    return;
  }
  if (migrationTask.sourceId === migrationTask.targetId) {
    ElMessage.warning('源数据源和目标数据源不能相同');
    return;
  }
  
  // 获取选中的表
  const checkedKeys = tableTreeRef.value ? tableTreeRef.value.getCheckedKeys() : [];
  migrationTask.table_names = checkedKeys.join(',');
  
  try {
    if (migrationTask.id) {
      // 更新现有任务
      await updateMigrationTask(migrationTask.id, migrationTask);
      ElMessage.success('任务更新成功！');
    } else {
      // 创建新任务
      await createMigrationTask(migrationTask);
      ElMessage.success('任务创建成功！');
    }
    
    // 重置表单
    resetTask();
    // 重新加载迁移任务列表
    loadMigrationTaskList();
  } catch (error) {
    console.error('保存任务失败:', error);
    ElMessage.error('保存任务失败：' + (error.response?.data?.detail || error.message));
  }
};

// 启动迁移任务
const startMigration = async (task) => {
  try {
    const response = await startMigrationTask(task.id);
    ElMessage.success('迁移任务已启动！');
    
    // 更新任务状态
    const index = migrationHistory.value.findIndex(t => t.id === task.id);
    if (index !== -1) {
      migrationHistory.value[index] = { ...migrationHistory.value[index], ...response.data };
    }
    
    // 轮询任务状态
    pollTaskStatus(task.id);
  } catch (error) {
    console.error('启动任务失败:', error);
    ElMessage.error('启动任务失败：' + (error.response?.data?.detail || error.message));
  }
};

// 停止迁移任务
const stopMigration = async (task) => {
  try {
    const response = await stopMigrationTask(task.id);
    ElMessage.success('迁移任务已停止！');
    
    // 更新任务状态
    const index = migrationHistory.value.findIndex(t => t.id === task.id);
    if (index !== -1) {
      migrationHistory.value[index] = { ...migrationHistory.value[index], ...response.data };
    }
  } catch (error) {
    console.error('停止任务失败:', error);
    ElMessage.error('停止任务失败：' + (error.response?.data?.detail || error.message));
  }
};

// 轮询任务状态
const pollTaskStatus = async (taskId) => {
  const poll = async () => {
    try {
      const response = await getMigrationTaskById(taskId);
      const task = response.data;
      
      // 更新任务状态
      const index = migrationHistory.value.findIndex(t => t.id === taskId);
      if (index !== -1) {
        migrationHistory.value[index] = task;
      }
      
      // 如果任务还在运行，继续轮询
      if (task.status === 'running') {
        setTimeout(poll, 1000);
      }
    } catch (error) {
      console.error('获取任务状态失败:', error);
    }
  };
  
  poll();
};

// 查看任务日志
const viewLog = async (task) => {
  try {
    const response = await getMigrationTaskById(task.id);
    const taskWithLog = response.data;
    
    ElMessageBox.alert(
      `<pre>${taskWithLog.log || '暂无日志信息'}</pre>`,
      `任务日志 - ${task.name}`,
      {
        dangerouslyUseHTMLString: true,
        showClose: true,
        confirmButtonText: '关闭',
        customClass: 'task-log-dialog'
      }
    );
  } catch (error) {
    if (error !== 'cancel') {
      console.error('查看日志失败:', error);
      ElMessage.error('查看日志失败：' + error.message);
    }
  }
};

// 重置任务表单
const resetTask = () => {
  Object.assign(migrationTask, {
    id: null,
    name: '',
    sourceId: null,
    targetId: null,
    migrate_structure: true,
    migrate_records: true,
    table_names: ''
  });
  tableTree.value = [];
  if (tableTreeRef.value) {
    tableTreeRef.value.setCheckedKeys([]);
  }
  currentEditingTask.value = null;
};

// 编辑任务
const editTask = (task) => {
  Object.assign(migrationTask, task);
  currentEditingTask.value = task.id;
  
  // 如果有选中的表，设置树的选中状态
  if (task.table_names) {
    const tableNames = task.table_names.split(',');
    if (tableTreeRef.value) {
      tableTreeRef.value.setCheckedKeys(tableNames);
    }
  }
};

// 删除任务
const deleteTask = async (task) => {
  try {
    await ElMessageBox.confirm(
      '此操作将永久删除该任务, 是否继续?',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    await deleteMigrationTask(task.id);
    ElMessage.success('任务删除成功！');
    // 重新加载迁移任务列表
    loadMigrationTaskList();
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除任务失败:', error);
      ElMessage.error('删除任务失败：' + (error.response?.data?.detail || error.message));
    }
  }
};

// 组件挂载时加载数据源列表和迁移任务列表
onMounted(() => {
  loadDataSourceList();
  loadMigrationTaskList();
});

// 监听数据源变化，自动更新任务列表
watch(dataSources, () => {
  loadMigrationTaskList();
}, { deep: true });
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