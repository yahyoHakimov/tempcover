<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup>
useHead({
  titleTemplate: (title) => (title ? `${title} — TempCover` : 'TempCover'),
})
</script>
