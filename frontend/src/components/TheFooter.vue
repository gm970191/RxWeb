<template>
  <el-footer class="footer">
    <div>
      <a href="#">友情链接1</a> | <a href="#">友情链接2</a> | <router-link to="/login">登录</router-link>
    </div>
    <div>
      &copy; {{ year }} {{ fullName }}. All Rights Reserved.
      <template v-if="beian">
        （<a v-if="beianUrl" :href="beianUrl" target="_blank" rel="noopener noreferrer">{{ beian }}</a><span v-else>{{ beian }}</span>）
      </template>
    </div>
  </el-footer>
</template>

<script>
import { site } from '../site'

export default {
  name: 'TheFooter',
  computed: {
    year() {
      return site.copyrightYear
    },
    fullName() {
      return site.fullName
    },
    beian() {
      return site.beian
    },
    beianUrl() {
      return site.beianUrl || ''
    },
  },
};
</script>

<style scoped>
.footer {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding: 24px;
  background: #0b3d73;
  color: rgba(255, 255, 255, 0.78);
  text-align: center;
  border-top: 3px solid #f0b429;
  font-size: 14px;
}
.footer a {
  color: #d6ecff;
  text-decoration: none;
  margin: 0 10px;
}
.footer a:hover {
  color: #f0b429;
}

@media (max-width: 768px) {
  .footer {
    padding: 20px 16px;
    font-size: 12px;
    line-height: 1.6;
  }

  .footer a {
    margin: 0 6px;
  }
}
</style> 