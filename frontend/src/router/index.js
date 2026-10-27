import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import ProductList from '../views/ProductList.vue';
import ProductDetail from '../views/ProductDetail.vue';
import News from '../views/News.vue';
import NewsDetail from '../views/NewsDetail.vue';
import Downloads from '../views/Downloads.vue';
import Contact from '../views/Contact.vue';
import Login from '../views/Login.vue';
import ForgotPassword from '../views/ForgotPassword.vue';
import ResetPassword from '../views/ResetPassword.vue';
import Account from '../views/Account.vue';
import Admin from '../views/Admin.vue';
import AdminNews from '../components/admin/AdminNews.vue';
import AdminProducts from '../components/admin/AdminProducts.vue';
import AdminMessages from '../components/admin/AdminMessages.vue';
import AdminLogs from '../components/admin/AdminLogs.vue';
import { useAuthStore } from '../stores/auth';

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/products', name: 'Products', component: ProductList },
  { path: '/products/:id', name: 'ProductDetail', component: ProductDetail },
  { path: '/news', name: 'News', component: News },
  { path: '/news/:id', name: 'NewsDetail', component: NewsDetail },
  { path: '/downloads', name: 'Downloads', component: Downloads },
  { path: '/contact', name: 'Contact', component: Contact },
  { path: '/login', name: 'Login', component: Login },
  { path: '/forgot-password', name: 'ForgotPassword', component: ForgotPassword },
  { path: '/reset-password', name: 'ResetPassword', component: ResetPassword },
  { path: '/account', name: 'Account', component: Account, meta: { requiresAuth: true } },
  {
    path: '/admin',
    component: Admin,
    meta: { requiresAuth: true, requiresAdmin: true },
    redirect: '/admin/news',
    children: [
      { path: 'news', name: 'AdminNews', component: AdminNews },
      { path: 'products', name: 'AdminProducts', component: AdminProducts },
      { path: 'messages', name: 'AdminMessages', component: AdminMessages },
      { path: 'logs', name: 'AdminLogs', component: AdminLogs },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (!auth.checked) {
    await auth.hydrate();
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'Login', query: { redirect: to.fullPath } };
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return auth.isAuthenticated ? { name: 'Account' } : { name: 'Login', query: { redirect: to.fullPath } };
  }
  if (to.name === 'Login' && auth.isAuthenticated) {
    return auth.homePath();
  }
  return true;
});

export default router;
