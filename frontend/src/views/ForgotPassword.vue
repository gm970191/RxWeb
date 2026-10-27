<template>
  <div class="login-page">
    <el-card class="login-card">
      <h1>重置密码</h1>
      <p class="login-hint">输入注册邮箱。配置了邮件服务时会发重置链接；未配置时会在本页显示链接。</p>
      <el-form @submit.prevent="handleSubmit">
        <el-form-item>
          <el-input v-model="email" placeholder="邮箱" size="large" />
        </el-form-item>
        <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleSubmit">发送重置说明</el-button>
      </el-form>
      <p v-if="message" class="result">{{ message }}</p>
      <p v-if="resetUrl" class="reset-url">
        邮件未发送，请打开此链接重置：<br />
        <router-link :to="resetPath">{{ resetUrl }}</router-link>
      </p>
      <div class="login-links">
        <router-link to="/login">返回登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { forgotPassword } from '../services/authService'

const email = ref('')
const loading = ref(false)
const message = ref('')
const resetUrl = ref('')
const resetPath = computed(() => {
  try {
    return resetUrl.value.replace(window.location.origin, '') || '/reset-password'
  } catch {
    return '/reset-password'
  }
})

async function handleSubmit() {
  if (!email.value.trim()) {
    ElMessage.warning('请输入邮箱')
    return
  }
  loading.value = true
  message.value = ''
  resetUrl.value = ''
  try {
    const data = await forgotPassword(email.value.trim())
    message.value = '如果该邮箱已注册，将收到重置说明。'
    if (data && data.reset_url) resetUrl.value = data.reset_url
  } catch (e) {
    ElMessage.error(e.message || '提交失败')
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
  margin: 0 0 8px;
  font-size: 24px;
  color: #0b3d73;
}

.login-hint,
.result {
  color: #606266;
  line-height: 1.6;
}

.login-btn {
  width: 100%;
}

.reset-url {
  margin-top: 16px;
  font-size: 13px;
  word-break: break-all;
}

.login-links {
  margin-top: 16px;
}

.login-links a {
  color: #1d6fb8;
  text-decoration: none;
}
</style>
