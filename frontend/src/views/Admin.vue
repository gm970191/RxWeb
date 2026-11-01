<template>
  <div v-if="auth.isAdmin" class="admin-container admin-page">
    <div class="admin-header">
      <div>
        <h1>管理后台</h1>
        <p>新闻、产品、留言和操作日志都在左侧菜单里。</p>
      </div>
      <div class="admin-user">
        <span>{{ auth.displayName }}</span>
        <el-button @click="passwordVisible = true">修改密码</el-button>
        <el-button @click="handleLogout">退出登录</el-button>
      </div>
    </div>
    <div class="admin-layout">
      <aside class="admin-side">
        <router-link
          v-for="item in menus"
          :key="item.path"
          :to="item.path"
          class="side-link"
          :class="{ active: isActive(item.path) }"
        >
          {{ item.label }}
        </router-link>
      </aside>
      <section class="admin-main">
        <router-view />
      </section>
    </div>

    <el-dialog v-model="passwordVisible" title="修改密码" width="420px" @closed="resetPasswordForm">
      <el-form :model="passwordForm" label-width="90px">
        <el-form-item label="当前密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password placeholder="至少 6 位" />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password @keyup.enter="handleChangePassword" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordVisible = false">取消</el-button>
        <el-button type="primary" :loading="passwordSaving" @click="handleChangePassword">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { changePassword } from '../services/authService'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const passwordVisible = ref(false)
const passwordSaving = ref(false)
const passwordForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })

const menus = [
  { path: '/admin/news', label: '新闻管理' },
  { path: '/admin/products', label: '产品管理' },
  { path: '/admin/messages', label: '留言管理' },
  { path: '/admin/logs', label: '操作日志' },
]

function isActive(path) {
  return route.path === path
}

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}

function resetPasswordForm() {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

async function handleChangePassword() {
  if (!passwordForm.oldPassword || !passwordForm.newPassword) {
    ElMessage.warning('请填写当前密码和新密码')
    return
  }
  if (passwordForm.newPassword.length < 6) {
    ElMessage.warning('新密码至少 6 位')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  passwordSaving.value = true
  try {
    await changePassword(passwordForm.oldPassword, passwordForm.newPassword)
    ElMessage.success('密码已更新')
    passwordVisible.value = false
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    passwordSaving.value = false
  }
}
</script>

<style scoped>
.admin-container {
  max-width: 1180px;
  margin: 24px auto;
  padding: 8px 0 24px;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.admin-header h1 {
  margin: 0 0 6px;
}

.admin-header p {
  margin: 0;
  color: #606266;
}

.admin-user {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #0b3d73;
  font-weight: 600;
}

.admin-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.admin-side {
  width: 180px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(11, 61, 115, 0.08);
}

.side-link {
  display: block;
  padding: 10px 12px;
  border-radius: 8px;
  color: #303133;
  text-decoration: none;
  font-weight: 500;
}

.side-link.active,
.side-link:hover {
  background: #e8f3ff;
  color: #0b3d73;
}

.admin-main {
  flex: 1;
  min-width: 0;
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 2px 10px rgba(11, 61, 115, 0.08);
}

@media (max-width: 768px) {
  .admin-container {
    margin: 8px auto;
    padding: 0;
  }

  .admin-header {
    flex-direction: column;
  }

  .admin-layout {
    flex-direction: column;
  }

  .admin-side {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
  }
}
</style>

<style>
.admin-page .admin-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.admin-page .admin-search {
  display: flex;
  align-items: center;
  gap: 8px;
}

.admin-page .admin-search .el-input {
  width: 240px;
}

.admin-page .admin-pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .admin-page .admin-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .admin-page .admin-search .el-input {
    width: 100%;
  }

  .admin-page .admin-pagination {
    justify-content: center;
  }
}
</style>
