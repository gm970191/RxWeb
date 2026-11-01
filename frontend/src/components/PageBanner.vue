<template>
  <section class="page-banner" :class="{ plain: !src }">
    <img v-if="src" :src="src" alt="" />
    <div v-if="src" class="veil"></div>
    <div class="banner-copy">
      <nav v-if="crumbs.length" class="crumb" aria-label="当前位置">
        <template v-for="(item, index) in crumbs" :key="`${item.label}-${index}`">
          <router-link v-if="item.to" :to="item.to">{{ item.label }}</router-link>
          <span v-else aria-current="page">{{ item.label }}</span>
          <span v-if="index < crumbs.length - 1" class="sep" aria-hidden="true">/</span>
        </template>
      </nav>
      <component :is="asHeading ? 'h1' : 'div'" v-if="title" class="banner-title">{{ title }}</component>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: { type: String, default: '' },
  image: { type: String, default: '' },
  asHeading: { type: Boolean, default: true },
  crumbs: { type: Array, default: () => [] },
})

const src = computed(() => (props.image || '').trim())
</script>

<style scoped>
.page-banner {
  position: relative;
  display: flex;
  align-items: flex-end;
  height: var(--rx-banner-height);
  margin-bottom: 28px;
  overflow: hidden;
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(11, 61, 115, 0.18);
}

.page-banner.plain {
  height: auto;
  align-items: center;
  background: linear-gradient(135deg, #0b3d73 0%, #1d6fb8 52%, #4aa3e0 100%);
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

.banner-copy {
  position: relative;
  z-index: 1;
  padding: 22px 28px;
}

.page-banner.plain .banner-copy {
  padding: 14px 28px;
}

.crumb {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0 0 8px;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.82);
}

.banner-copy .crumb:last-child {
  margin-bottom: 0;
}

.crumb a {
  color: #fff;
  text-decoration: none;
}

.crumb a:hover {
  color: #f0b429;
}

.sep {
  color: rgba(255, 255, 255, 0.55);
}

.banner-title {
  margin: 0;
  font-size: 32px;
  font-weight: 600;
  line-height: 1.25;
  color: #fff;
  text-shadow: 0 2px 10px rgba(11, 61, 115, 0.45);
}

@media (max-width: 768px) {
  .page-banner {
    margin-bottom: 20px;
  }

  .banner-copy,
  .page-banner.plain .banner-copy {
    padding: 12px 16px;
  }

  .banner-title {
    font-size: 26px;
  }
}
</style>
