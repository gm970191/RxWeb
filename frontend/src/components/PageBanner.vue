<template>
  <section v-if="image" class="page-banner">
    <img :src="image" alt="" />
    <div class="veil"></div>
    <h1>{{ title }}</h1>
  </section>
  <h1 v-else class="plain-title">{{ title }}</h1>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  image: { type: String, default: '' },
})
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

.page-banner h1,
.plain-title {
  margin: 0;
  font-size: 32px;
  color: #0b3d73;
}

.page-banner h1 {
  position: relative;
  z-index: 1;
  padding: 24px 28px;
  color: #fff;
  text-shadow: 0 2px 10px rgba(11, 61, 115, 0.45);
}

@media (max-width: 768px) {
  .page-banner {
    height: 160px;
    margin-bottom: 20px;
  }

  .page-banner h1,
  .plain-title {
    font-size: 26px;
  }

  .page-banner h1 {
    padding: 16px;
  }
}
</style>
