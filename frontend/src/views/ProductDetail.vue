<template>
  <div class="product-detail-container">
    <nav class="crumb" aria-label="当前位置">
      <router-link to="/products">产品中心</router-link>
      <span class="sep" aria-hidden="true">/</span>
      <span aria-current="page">详情</span>
    </nav>
    <el-card v-if="product">
      <div class="detail-layout">
        <div class="image-section">
          <div
            class="image-zoomer-wrapper"
            @mousemove="onMouseMove"
            @mouseleave="onMouseLeave"
          >
            <img :src="product.image" class="main-image" ref="imgRef" alt="" />
            <div v-if="showZoom" class="zoom-lens" :style="lensStyle"></div>
          </div>
          <teleport to="body">
            <div v-if="showZoom" class="zoom-result" :style="zoomResultStyle">
              <img :src="product.image" class="zoom-image" alt="" :style="zoomImgStyle" />
            </div>
          </teleport>
        </div>
        <div class="info-section">
          <h1 class="product-title">{{ product.name }}</h1>
          <div class="product-desc">{{ product.description }}</div>
        </div>
      </div>
    </el-card>
    <el-empty v-else description="未找到该产品" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchProductDetail, getMockProducts } from '../services/productService'

const route = useRoute()
const product = ref(null)

onMounted(async () => {
  try {
    product.value = await fetchProductDetail(route.params.id)
  } catch {
    const allProducts = await getMockProducts()
    product.value = allProducts.find(item => String(item.id) === route.params.id)
  }
})

// 放大镜功能
const showZoom = ref(false)
const lensStyle = ref({})
const zoomResultStyle = ref({})
const zoomImgStyle = ref({})
const imgRef = ref(null)

function onMouseMove(e) {
  if (window.matchMedia('(max-width: 768px)').matches) return
  const img = imgRef.value
  if (!img) return
  const rect = img.getBoundingClientRect()
  if (!rect.width || !rect.height) return

  const nw = img.naturalWidth || rect.width
  const nh = img.naturalHeight || rect.height
  const fit = Math.min(rect.width / nw, rect.height / nh)
  const dispW = nw * fit
  const dispH = nh * fit
  const padX = (rect.width - dispW) / 2
  const padY = (rect.height - dispH) / 2

  const roomRight = window.innerWidth - rect.right - 28
  const roomBelow = window.innerHeight - rect.bottom - 28
  const zoom = 4
  let panel = 520
  const placeRight = roomRight >= 320
  if (placeRight) {
    panel = Math.min(560, roomRight)
  } else if (roomBelow >= 280) {
    panel = Math.min(560, roomBelow)
  } else {
    showZoom.value = false
    return
  }
  const lensSize = Math.min(dispW, dispH, panel / zoom)
  const x = e.clientX - rect.left - padX
  const y = e.clientY - rect.top - padY
  const lensX = Math.max(0, Math.min(x - lensSize / 2, dispW - lensSize))
  const lensY = Math.max(0, Math.min(y - lensSize / 2, dispH - lensSize))

  showZoom.value = true
  lensStyle.value = {
    left: `${padX + lensX}px`,
    top: `${padY + lensY}px`,
    width: `${lensSize}px`,
    height: `${lensSize}px`,
  }
  const left = placeRight
    ? rect.right + 16
    : Math.max(12, Math.min(rect.left, window.innerWidth - panel - 12))
  const top = placeRight
    ? Math.max(12, Math.min(rect.top, window.innerHeight - panel - 12))
    : rect.bottom + 12
  zoomResultStyle.value = {
    left: `${left}px`,
    top: `${top}px`,
    width: `${panel}px`,
    height: `${panel}px`,
  }
  zoomImgStyle.value = {
    width: `${dispW * zoom}px`,
    height: `${dispH * zoom}px`,
    left: `${-lensX * zoom}px`,
    top: `${-lensY * zoom}px`,
  }
}
function onMouseLeave() {
  showZoom.value = false
}
</script>

<style scoped>
.product-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  display: block;
  padding-top: 8px;
  padding-bottom: 32px;
}
.crumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px;
  font-size: 15px;
  color: #909399;
}
.crumb a {
  color: #0b3d73;
  text-decoration: none;
}
.crumb a:hover {
  color: #1d6fb8;
}
.sep {
  color: #c0c4cc;
}
.detail-layout {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}
.image-section {
  position: relative;
  width: 420px;
  min-width: 280px;
  flex: none;
}
.image-zoomer-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  background: #f4f7fb;
  border-radius: 8px;
  cursor: crosshair;
}
.main-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: 8px;
}
.zoom-lens {
  position: absolute;
  pointer-events: none;
  border: 1px solid rgba(11, 61, 115, 0.55);
  background: rgba(255, 255, 255, 0.28);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.7);
}
.zoom-result {
  position: fixed;
  z-index: 40;
  overflow: hidden;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #f4f7fb;
  box-shadow: 0 16px 40px rgba(11, 61, 115, 0.22);
  pointer-events: none;
}
.zoom-image {
  position: absolute;
  max-width: none;
  max-height: none;
  object-fit: fill;
}
.info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.product-title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 16px;
}
.product-desc {
  font-size: 16px;
  color: #606266;
  line-height: 1.8;
}

@media (max-width: 768px) {
  .product-detail-container {
    padding-top: 8px;
    padding-bottom: 16px;
    min-height: auto;
  }

  .detail-layout {
    flex-direction: column;
    gap: 16px;
  }

  .image-section,
  .image-zoomer-wrapper {
    width: 100%;
    min-width: 0;
    height: auto;
  }

  .image-zoomer-wrapper {
    max-width: 100%;
    aspect-ratio: 1;
  }

  .main-image {
    height: 100%;
  }

  .zoom-lens,
  .zoom-result {
    display: none;
  }

  .product-title {
    font-size: 22px;
  }
}
</style> 