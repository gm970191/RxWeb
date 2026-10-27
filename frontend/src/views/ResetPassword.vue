<template>
  <div class="login-page">
    <el-card class="login-card">
      <h1>设置新密码</h1>
      <el-form @submit.prevent="handleSubmit">
        <el-form-item>
          <el-input v-model="password" type="password" placeholder="新密码（至少 6 位）" show-password size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="confirm" type="password" placeholder="再次输入新密码" show-password size="large" />
        </el-form-item>
        <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleSubmit">保存新密码</el-button>
      </el-form>
      <div class="login-links">
        <router-link to="/login">返回登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { resetPassword } from '../services/authService'

const route = useRoute()
const router = useRouter()
const password = ref('')
const confirm = ref('')
const loading = ref(false)

async function handleSubmit() {
  const token = String(route.query.token || '')
  if (!token) {
    ElMessage.error('重置链接无效')
    return
  }
  if (password.value.length < 6) {
    ElMessage.warning('密码至少 6 位')
    return
  }
  if (password.value !== confirm.value) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  loading.value = true
  try {
    await resetPassword(token, password.value)
    ElMessage.success('密码已重置，请登录')
    router.replace('/login')
  } catch (e) {
    ElMessage.error(e.message || '重置失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  max-width: 420px;
  margin: 48px auto;
  padding: 0 8px;
}

.login-card {
  border-radius: 12px;
}

.login-card h1 {
  margin: 0 0 16px;
  font-size: 24px;
  color: #0b3d73;
}

.login-btn {
  width: 100%;
}

.login-links {
  margin-top: 16px;
}

.login-links a {
  color: #1d6fb8;
  text-decoration: none;
}
</style>
