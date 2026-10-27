<template>
  <div class="login-page">
    <el-card class="login-card">
      <h1>{{ mode === 'register' ? '注册账号' : '登录' }}</h1>
      <p class="login-hint">
        使用邮箱登录。管理员可进入后台；普通用户可查看自己提交的留言。
      </p>
      <el-form @submit.prevent="handleSubmit">
        <el-form-item v-if="mode === 'register'">
          <el-input v-model="form.name" placeholder="姓名" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.email" placeholder="邮箱" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" show-password size="large" @keyup.enter="handleSubmit" />
        </el-form-item>
        <el-button type="primary" size="large" class="login-btn" :loading="loading" @click="handleSubmit">
          {{ mode === 'register' ? '注册并登录' : '登录' }}
        </el-button>
      </el-form>
      <div class="login-links">
        <a href="#" @click.prevent="mode = mode === 'register' ? 'login' : 'register'">
          {{ mode === 'register' ? '已有账号？去登录' : '没有账号？去注册' }}
        </a>
        <router-link to="/forgot-password">忘记密码</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const loading = ref(false)
const mode = ref('login')
const form = reactive({ email: '', password: '', name: '' })

function nextPath() {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : ''
  if (redirect.startsWith('/admin') && !auth.isAdmin) return auth.homePath()
  if (redirect.startsWith('/')) return redirect
  return auth.homePath()
}

async function handleSubmit() {
  if (!form.email || !form.password) {
    ElMessage.warning('请输入邮箱和密码')
    return
  }
  loading.value = true
  try {
    if (mode.value === 'register') {
      await auth.register({ email: form.email.trim(), password: form.password, name: form.name.trim() })
      ElMessage.success('注册成功')
    } else {
      await auth.login(form.email.trim(), form.password)
      ElMessage.success('登录成功')
    }
    router.replace(nextPath())
  } catch (e) {
    ElMessage.error(e.message || '操作失败')
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

.login-hint {
  margin: 0 0 20px;
  color: #606266;
  line-height: 1.6;
}

.login-btn {
  width: 100%;
}

.login-links {
  display: flex;
  justify-content: space-between;
  margin-top: 14px;
  font-size: 13px;
}

.login-links a {
  color: #1d6fb8;
  text-decoration: none;
}

@media (max-width: 768px) {
  .login-page {
    margin: 16px auto;
  }
}
</style>
