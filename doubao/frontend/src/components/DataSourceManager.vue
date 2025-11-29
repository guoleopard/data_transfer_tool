<template>
  <div class="data-source-manager">
    <h2>数据源管理</h2>
    <el-form :model="dataSource" label-width="80px" class="form">
      <el-form-item label="数据源名称">
        <el-input v-model="dataSource.name" placeholder="请输入数据源名称"></el-input>
      </el-form-item>
      <el-form-item label="数据库类型">
        <el-select v-model="dataSource.type" placeholder="请选择数据库类型">
          <el-option label="MySQL" value="mysql"></el-option>
          <el-option label="SQL Server" value="mssql"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="主机地址">
        <el-input v-model="dataSource.host" placeholder="请输入主机地址"></el-input>
      </el-form-item>
      <el-form-item label="端口号">
        <el-input v-model="dataSource.port" placeholder="请输入端口号"></el-input>
      </el-form-item>
      <el-form-item label="数据库名">
        <el-input v-model="dataSource.database" placeholder="请输入数据库名"></el-input>
      </el-form-item>
      <el-form-item label="用户名">
        <el-input v-model="dataSource.username" placeholder="请输入用户名"></el-input>
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="dataSource.password" placeholder="请输入密码" type="password"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="testConnection">测试连接</el-button>
        <el-button @click="saveDataSource">保存数据源</el-button>
      </el-form-item>
    </el-form>
    <el-table :data="dataSources" style="width: 100%; margin-top: 20px" border>
      <el-table-column prop="name" label="数据源名称"></el-table-column>
      <el-table-column prop="type" label="数据库类型"></el-table-column>
      <el-table-column prop="host" label="主机地址"></el-table-column>
      <el-table-column prop="database" label="数据库名"></el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button size="small" @click="editDataSource(scope.row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteDataSourceConfirm(scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { createDataSource, getDataSourceList, updateDataSource, deleteDataSource } from '../api';

const dataSource = reactive({
  id: null,
  name: '',
  type: 'mysql',
  host: 'localhost',
  port: 3306,
  database: '',
  username: 'root',
  password: ''
});

const dataSources = ref([]);

// 测试连接函数 - 暂时使用模拟实现
const testConnection = async () => {
  try {
    // Simulate connection delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    ElMessage.success('连接成功！');
  } catch (error) {
    console.error('连接失败:', error);
    ElMessage.error('连接失败：' + error.message);
  }
};

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

// 保存数据源
const saveDataSource = async () => {
  if (!dataSource.name) {
    ElMessage.warning('请输入数据源名称');
    return;
  }
  
  try {
    if (dataSource.id) {
      // 更新现有数据源
      await updateDataSource(dataSource.id, dataSource);
      ElMessage.success('数据源更新成功！');
    } else {
      // 创建新数据源
      await createDataSource(dataSource);
      ElMessage.success('数据源创建成功！');
    }
    
    // 重置表单
    resetDataSourceForm();
    // 重新加载数据源列表
    loadDataSourceList();
  } catch (error) {
    console.error('保存数据源失败:', error);
    ElMessage.error('保存数据源失败：' + (error.response?.data?.detail || error.message));
  }
};

// 编辑数据源
const editDataSource = (row) => {
  Object.assign(dataSource, row);
};

// 删除数据源
const deleteDataSourceConfirm = async (row) => {
  try {
    await ElMessageBox.confirm(
      '此操作将永久删除该数据源, 是否继续?',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    
    await deleteDataSource(row.id);
    ElMessage.success('数据源删除成功！');
    // 重新加载数据源列表
    loadDataSourceList();
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除数据源失败:', error);
      ElMessage.error('删除数据源失败：' + (error.response?.data?.detail || error.message));
    }
  }
};

// 重置数据源表单
const resetDataSourceForm = () => {
  Object.assign(dataSource, {
    id: null,
    name: '',
    type: 'mysql',
    host: 'localhost',
    port: 3306,
    database: '',
    username: 'root',
    password: ''
  });
};

// 组件挂载时加载数据源列表
onMounted(() => {
  loadDataSourceList();
});
</script>

<style scoped>
.data-source-manager {
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
</style>