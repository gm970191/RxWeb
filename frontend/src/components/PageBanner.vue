<template>
  <section class="page-banner">
    <img :src="src" alt="" />
    <div class="veil"></div>
    <component :is="asHeading ? 'h1' : 'div'" class="banner-title">{{ title }}</component>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { defaultPageBanner } from '../sharedMedia'

const props = defineProps({
  title: { type: String, default: '' },
  image: { type: String, default: '' },
  asHeading: { type: Boolean, default: true },
})

const src = computed(() => props.image || defaultPageBanner)
</script>

<style scoped>
.page-banner {
  position: relative;
  display: flex;
  align-items: flex-end;
  height: 220px;
  margin-bottom: 28px;
  overflow: hidden;
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(11, 61, 115, 0.18);
}

.page-banner img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.veil {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(11, 61, 115, 0.08) 35%, rgba(11, 61, 115, 0.72) 100%);
}

.banner-title {
  position: relative;
  z-index: 1;
  margin: 0;
  padding: 24px 28px;
  font-size: 32px;
  font-weight: 600;
  color: #fff;
  text-shadow: 0 2px 10px rgba(11, 61, 115, 0.45);
}

@media (max-width: 768px) {
  .page-banner {
    height: 160px;
    margin-bottom: 20px;
  }

  .banner-title {
    padding: 16px;
    font-size: 26px;
  }
}
</style>
