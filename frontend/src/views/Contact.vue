<template>
  <div class="contact-container">
    <el-row :gutter="40">
      <el-col :xs="24" :sm="24" :md="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>联系信息</span>
            </div>
          </template>
          <div class="contact-info">
            <p v-for="item in site.contact" :key="item.label">
              <strong>{{ item.label }}：</strong> {{ item.value }}
            </p>
            <div v-if="site.wechatQr" class="wechat">
              <img :src="site.wechatQr" alt="微信二维码" />
              <p>扫一扫，关注我们</p>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12">
        <el-card class="box-card">
          <template #header>
            <div class="card-header">
              <span>在线留言</span>
            </div>
          </template>
          <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
            <el-form-item label="您的姓名" prop="name">
              <el-input v-model="form.name" />
            </el-form-item>
            <el-form-item label="您的邮箱" prop="email">
              <el-input v-model="form.email" />
            </el-form-item>
            <el-form-item label="主题" prop="subject">
              <el-input v-model="form.subject" />
            </el-form-item>
            <el-form-item label="留言内容" prop="message">
              <el-input v-model="form.message" type="textarea" :rows="4" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSubmit">提交</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createMessage } from '../services/messageService'
import { useAuthStore } from '../stores/auth'
import { site } from '../site'

const auth = useAuthStore()
const formRef = ref(null)
const form = ref({
  name: '',
  email: '',
  subject: '',
  message: '',
})

onMounted(() => {
  if (auth.isAuthenticated) {
    form.value.email = auth.email
    form.value.name = auth.name || form.value.name
  }
})

const rules = {
  name: [{ required: true, message: '请输入您的姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入您的邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] },
  ],
  subject: [{ required: true, message: '请输入主题', trigger: 'blur' }],
  message: [{ required: true, message: '请输入留言内容', trigger: 'blur' }],
}

const handleSubmit = () => {
  formRef.value.validate(async (valid) => {
    if (!valid) {
      ElMessage.error('请检查表单输入。')
      return false
    }
    try {
      await createMessage({
        name: form.value.name,
        email: form.value.email,
        subject: form.value.subject,
        content: form.value.message,
      })
      ElMessage.success(auth.isAuthenticated ? '留言提交成功，可在“我的留言”中查看。' : '留言提交成功，我们会尽快回复。')
      form.value = {
        name: auth.name || '',
        email: auth.email || '',
        subject: '',
        message: '',
      }
    } catch (e) {
      ElMessage.error(e.message || '留言提交失败')
    }
  })
}
</script>

<style scoped>
.contact-container {
  max-width: 1200px;
  margin: auto;
  padding: 24px 0;
}
.card-header {
  font-size: 20px;
  font-weight: bold;
}
.contact-info p {
  margin: 0 0 16px;
  line-height: 1.6;
}
.wechat {
  margin-top: 8px;
}
.wechat img {
  width: 140px;
  height: 140px;
  object-fit: contain;
  background: #fff;
}
.wechat p {
  margin-top: 8px;
  color: #606266;
}

@media (max-width: 768px) {
  .contact-container {
    padding: 8px 0 16px;
  }

  .contact-container :deep(.el-col) {
    margin-bottom: 16px;
  }

  .contact-info p {
    word-break: break-word;
  }
}
</style> 