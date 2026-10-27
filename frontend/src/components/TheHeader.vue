<template>
  <el-header class="header">
    <router-link to="/" class="logo" @click="mobileOpen = false">
      <span class="logo-mark"></span>
      瑞学软件
    </router-link>
    <el-menu mode="horizontal" :router="true" :default-active="activeMenu" class="nav-menu desktop-nav">
      <el-menu-item v-for="item in navItems" :key="item.path" :index="item.path">
        {{ item.label }}
      </el-menu-item>
      <el-menu-item v-if="auth.isAdmin" index="/admin/news">后台</el-menu-item>
      <el-menu-item v-else-if="auth.isAuthenticated" index="/account">我的留言</el-menu-item>
      <el-menu-item v-else index="/login">登录</el-menu-item>
    </el-menu>
    <button
      class="menu-toggle"
      type="button"
      :class="{ open: mobileOpen }"
      :aria-expanded="mobileOpen"
      aria-label="打开导航菜单"
      @click="mobileOpen = !mobileOpen"
    >
      <span></span>
      <span></span>
      <span></span>
    </button>
    <div v-if="mobileOpen" class="mobile-backdrop" @click="mobileOpen = false"></div>
    <nav v-if="mobileOpen" class="mobile-nav" aria-label="手机导航">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="mobile-nav-link"
        :class="{ active: isActive(item.path) }"
        @click="mobileOpen = false"
      >
        {{ item.label }}
      </router-link>
      <router-link
        v-if="auth.isAdmin"
        to="/admin/news"
        class="mobile-nav-link"
        :class="{ active: isActive('/admin') }"
        @click="mobileOpen = false"
      >
        后台
      </router-link>
      <router-link
        v-else-if="auth.isAuthenticated"
        to="/account"
        class="mobile-nav-link"
        :class="{ active: isActive('/account') }"
        @click="mobileOpen = false"
      >
        我的留言
      </router-link>
      <router-link
        v-else
        to="/login"
        class="mobile-nav-link"
        :class="{ active: isActive('/login') }"
        @click="mobileOpen = false"
      >
        登录
      </router-link>
    </nav>
  </el-header>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const auth = useAuthStore()
const mobileOpen = ref(false)
const activeMenu = computed(() => {
  if (route.path.startsWith('/admin')) return '/admin/news'
  return route.path
})

const navItems = [
  { path: '/', label: '主页' },
  { path: '/products', label: '产品中心' },
  { path: '/news', label: '新闻动态' },
  { path: '/downloads', label: '资源下载' },
  { path: '/contact', label: '联系我们' },
]

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path === path || route.path.startsWith(`${path}/`)
}

watch(() => route.fullPath, () => {
  mobileOpen.value = false
})
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
  height: 64px;
  position: sticky;
  top: 0;
  z-index: 20;
  color: #fff;
  background: linear-gradient(90deg, #0b3d73 0%, #1d6fb8 55%, #2b8fd4 100%);
  box-shadow: 0 8px 24px rgba(11, 61, 115, 0.28);
  border-bottom: 3px solid #f0b429;
  overflow: visible;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 1px;
  color: #fff;
  white-space: nowrap;
  text-decoration: none;
}

.logo-mark {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  background: #f0b429;
  box-shadow: 0 0 0 4px rgba(240, 180, 41, 0.22);
}

.nav-menu {
  flex-grow: 1;
  justify-content: flex-end;
  border-bottom: none;
  background: transparent;
  --el-menu-bg-color: transparent;
  --el-menu-text-color: rgba(255, 255, 255, 0.9);
  --el-menu-hover-bg-color: rgba(255, 255, 255, 0.14);
  --el-menu-active-color: #ffe08a;
  --el-menu-hover-text-color: #fff;
  --el-menu-border-color: transparent;
}

.el-menu-item {
  font-size: 16px;
  font-weight: 500;
}

.nav-menu :deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.12) !important;
  border-bottom-color: #f0b429 !important;
}

.menu-toggle {
  display: none;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
  width: 40px;
  height: 40px;
  padding: 8px;
  border: 0;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.12);
  cursor: pointer;
}

.menu-toggle span {
  display: block;
  height: 2px;
  width: 100%;
  background: #fff;
  border-radius: 2px;
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.menu-toggle.open span:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.menu-toggle.open span:nth-child(2) {
  opacity: 0;
}

.menu-toggle.open span:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

.mobile-backdrop,
.mobile-nav {
  display: none;
}

@media (max-width: 768px) {
  .header {
    padding: 0 16px;
    height: 56px;
  }

  .logo {
    font-size: 18px;
  }

  .desktop-nav {
    display: none !important;
  }

  .menu-toggle {
    display: flex;
  }

  .mobile-backdrop {
    display: block;
    position: fixed;
    inset: 56px 0 0 0;
    background: rgba(11, 61, 115, 0.35);
    z-index: 30;
  }

  .mobile-nav {
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 56px;
    left: 0;
    right: 0;
    padding: 8px 12px 16px;
    background: #0b3d73;
    box-shadow: 0 12px 24px rgba(11, 61, 115, 0.28);
    z-index: 31;
  }

  .mobile-nav-link {
    display: block;
    padding: 12px 14px;
    color: rgba(255, 255, 255, 0.92);
    text-decoration: none;
    font-size: 16px;
    font-weight: 500;
    border-radius: 8px;
  }

  .mobile-nav-link.active,
  .mobile-nav-link:hover {
    background: rgba(255, 255, 255, 0.12);
    color: #ffe08a;
  }
}
</style>
