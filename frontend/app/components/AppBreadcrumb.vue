<template>
  <nav class="breadcrumb" aria-label="Breadcrumb">
    <ol class="breadcrumb-list">
      <li
        v-for="(item, index) in items"
        :key="index"
        class="breadcrumb-item"
      >
        <!-- Separator (not shown before first item) -->
        <span v-if="index > 0" class="breadcrumb-sep" aria-hidden="true">›</span>

        <!-- Clickable link -->
        <NuxtLink v-if="item.to" :to="item.to" class="breadcrumb-link">
          {{ item.label }}
        </NuxtLink>

        <!-- Current page (no link) -->
        <span v-else class="breadcrumb-current">{{ item.label }}</span>
      </li>
    </ol>
  </nav>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    required: true,
    // Each item: { label: string, to?: string }
  },
})
</script>

<style scoped>
.breadcrumb {
  margin-bottom: 1.5rem;
}

.breadcrumb-list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.25rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.breadcrumb-sep {
  font-size: 1.1rem;
  color: var(--text-muted, #aaa);
  font-weight: 400;
  line-height: 1;
  margin: 0 0.15rem;
}

.breadcrumb-link {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--text-muted, #888);
  text-decoration: none;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  transition: all 0.15s;
}
.breadcrumb-link:hover {
  color: var(--brand-700, #CC4100);
  background: var(--brand-50, #FFF7F2);
}

.breadcrumb-current {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary, #1F2937);
  padding: 0.25rem 0.5rem;
}
</style>
