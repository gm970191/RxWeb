<template>
  <div class="home-container">
    <!-- Hero Section -->
    <el-carousel v-if="banners.length" class="home-banner" height="320px" indicator-position="outside">
      <el-carousel-item v-for="image in banners" :key="image">
        <img :src="image" class="banner-img" alt="" />
      </el-carousel-item>
    </el-carousel>

    <div class="hero-section">
      <div class="hero-content">
        <h1>{{ site.heroTitle }}</h1>
        <p>{{ site.heroLead }}</p>
        <p v-if="site.hotline" class="hotline">{{ site.hotline }}</p>
        <el-button type="primary" size="large" @click="goToProducts">浏览产品</el-button>
      </div>
    </div>

    <!-- Featured Products Section -->
    <div class="featured-section">
      <h2>特色产品</h2>
      <el-row :gutter="20">
        <el-col v-for="product in featuredProducts" :key="product.id" :xs="24" :sm="12" :md="8">
          <el-card class="product-card" @click="router.push(`/products/${product.id}`)">
            <img :src="product.image" class="product-image" />
            <div class="product-info">
              <h3>{{ product.name }}</h3>
              <p class="desc">{{ product.description }}</p>
              <div class="price">{{ formatPrice(product.price) }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Latest News Section -->
    <div class="featured-section">
      <h2>最新动态</h2>
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card>
            <div v-for="item in latestNews" :key="item.id" class="news-item-home" @click="goToNews(item.id)">
              <span class="news-date">{{ item.date }}</span>
              <span class="news-title-home">{{ item.title }}</span>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchProducts, getMockProducts } from '../services/productService'
import { fetchNews, getMockNews } from '../services/newsService'
import { site } from '../site'
import { formatPrice } from '../utils/price'

const router = useRouter()
const featuredProducts = ref([])
const latestNews = ref([])
const banners = site.banners || []

function pickFeatured(list) {
  const ids = site.featuredProductIds || []
  if (!ids.length) return (list || []).slice(0, 3)
  const picked = ids.map((id) => (list || []).find((item) => item.id === id)).filter(Boolean)
  return picked.length ? picked : (list || []).slice(0, 3)
}

onMounted(async () => {
  try {
    featuredProducts.value = pickFeatured(await fetchProducts())
  } catch {
    featuredProducts.value = pickFeatured(await getMockProducts())
  }

  try {
    const data = await fetchNews({ page: 1, pageSize: 3, source: site.defaultNewsSource || '' })
    latestNews.value = data.list || []
  } catch {
    const mock = await getMockNews()
    latestNews.value = site.defaultNewsSource
      ? mock.filter((item) => item.source === site.defaultNewsSource).slice(0, 3)
      : mock.slice(0, 3)
  }
})

const goToProducts = () => {
  router.push('/products')
}

const goToNews = (id) => {
  router.push({ name: 'NewsDetail', params: { id } })
}
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: auto;
  padding: 24px 0 40px 0;
}
.hero-section {
  background: linear-gradient(135deg, #0b3d73 0%, #1d6fb8 52%, #4aa3e0 100%);
  padding: 80px 40px;
  text-align: center;
  margin-bottom: 40px;
  border-radius: 12px;
  color: #fff;
  box-shadow: 0 12px 32px rgba(11, 61, 115, 0.22);
}
.hero-content h1 {
  font-size: 36px;
  margin-bottom: 16px;
  color: #fff;
}
.hero-content p {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.88);
  margin-bottom: 24px;
}
.hotline {
  margin-top: -8px;
  font-weight: 600;
}
.home-banner {
  margin-bottom: 24px;
}
.banner-img {
  width: 100%;
  height: 320px;
  object-fit: cover;
  display: block;
}

.featured-section {
  max-width: 1200px;
  margin: auto;
  padding: 0 24px 40px;
}
.featured-section h2 {
  text-align: center;
  font-size: 28px;
  margin-bottom: 32px;
}

.product-card {
  width: 100%;
  cursor: pointer;
}
.product-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}
.product-info {
  padding: 14px;
}
.price {
  color: #e4393c;
  font-weight: bold;
  margin-top: 8px;
}
.desc {
  color: #888;
  font-size: 13px;
  height: 40px; /* 限制描述高度，保持对齐 */
  overflow: hidden;
}

.news-item-home {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #EBEEF5;
  font-size: 15px;
}
.news-item-home:last-child {
  border-bottom: none;
}
.news-date {
  color: #909399;
  margin-right: 20px;
}
.news-title-home {
  flex-grow: 1;
  color: #303133;
  cursor: pointer;
}
.news-title-home:hover {
  color: #409EFF;
}

@media (max-width: 768px) {
  .home-container {
    padding: 0 0 24px;
  }

  .hero-section {
    padding: 40px 16px;
    margin-bottom: 24px;
    border-radius: 10px;
  }

  .hero-content h1 {
    font-size: 26px;
  }

  .hero-content p {
    font-size: 15px;
    line-height: 1.6;
  }

  .featured-section {
    padding: 0 0 24px;
  }

  .featured-section h2 {
    font-size: 22px;
    margin-bottom: 20px;
  }

  .product-card {
    margin-bottom: 16px;
  }

  .product-image {
    height: 180px;
  }

  .news-item-home {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .news-date {
    margin-right: 0;
    font-size: 13px;
  }
}
</style> 