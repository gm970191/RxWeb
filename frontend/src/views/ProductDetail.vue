<template>
  <div class="product-detail-container">
    <el-card v-if="product">
      <div class="detail-layout">
        <div class="image-section">
          <div class="image-zoomer-wrapper">
            <img
              :src="product.image"
              class="main-image"
              @mousemove="onMouseMove"
              @mouseleave="onMouseLeave"
              ref="imgRef"
            />
            <div v-if="showZoom" class="zoom-lens" :style="lensStyle"></div>
            <div v-if="showZoom" class="zoom-result" :style="zoomResultStyle">
              <img :src="product.image" :style="zoomImgStyle" />
            </div>
          </div>
        </div>
        <div class="info-section">
          <h1 class="product-title">{{ product.name }}</h1>
          <div class="product-price">{{ formatPrice(product.price) }}</div>
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
import { formatPrice } from '../utils/price'

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
  showZoom.value = true
  const img = imgRef.value
  const rect = img.getBoundingClientRect()
  const lensSize = 100 // 放大镜区域更大
  const zoom = 2.5
  // 放大区宽高与图片等比，且更大
  const zoomBoxWidth = rect.width * 1.6
  const zoomBoxHeight = rect.height * 1.6

  // 限制 lens 不超出图片且保证放大区无留白
  let x = e.clientX - rect.left
  let y = e.clientY - rect.top
  let lensX = x - lensSize / 2
  let lensY = y - lensSize / 2
  // 限制 lens 范围，保证放大区无留白
  lensX = Math.max(0, Math.min(lensX, rect.width - lensSize))
  lensY = Math.max(0, Math.min(lensY, rect.height - lensSize))

  lensStyle.value = {
    left: lensX + 'px',
    top: lensY + 'px',
    width: lensSize + 'px',
    height: lensSize + 'px',
    position: 'absolute',
    border: '1.5px solid #409EFF',
    background: 'rgba(64,158,255,0.1)',
    pointerEvents: 'none',
    zIndex: 2
  }
  zoomResultStyle.value = {
    left: rect.width + 40 + 'px',
    top: 0,
    width: zoomBoxWidth + 'px',
    height: zoomBoxHeight + 'px',
    position: 'absolute',
    border: '1px solid #eee',
    background: '#fff',
    overflow: 'hidden',
    zIndex: 3,
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
    borderRadius: '8px'
  }
  // 限制放大图片的偏移，保证放大区无留白
  let imgLeft = -lensX * zoom
  let imgTop = -lensY * zoom
  // 限制最大偏移，防止留白
  const maxLeft = -(rect.width * zoom - zoomBoxWidth)
  const maxTop = -(rect.height * zoom - zoomBoxHeight)
  if (imgLeft < maxLeft) imgLeft = maxLeft
  if (imgTop < maxTop) imgTop = maxTop
  if (imgLeft > 0) imgLeft = 0
  if (imgTop > 0) imgTop = 0
  zoomImgStyle.value = {
    position: 'absolute',
    left: imgLeft + 'px',
    top: imgTop + 'px',
    width: rect.width * zoom + 'px',
    height: rect.height * zoom + 'px',
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
  padding-top: 32px;
  padding-bottom: 32px;
}
.detail-layout {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}
.image-section {
  position: relative;
  width: 360px;
  min-width: 320px;
  height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.image-zoomer-wrapper {
  position: relative;
  width: 320px;
  height: 320px;
}
.main-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.zoom-lens {
  pointer-events: none;
  border-radius: 4px;
}
.zoom-result {
  /* 具体宽高由内联样式控制 */
  position: absolute;
  top: 0;
  left: 344px;
  background: #fff;
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
.product-price {
  color: #e4393c;
  font-size: 22px;
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

  .product-price {
    font-size: 20px;
  }
}
</style> 