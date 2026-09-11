<template>
  <header class="tc-topbar">
    <div class="tc-topbar-inner">
      <NuxtLink :to="homeTo" class="tc-brand" aria-label="TempCover home">
        <img src="/tempcover-logo-white.png" alt="TempCover" class="tc-brand-logo" />
        <span v-if="roleLabel" class="tc-role">{{ roleLabel }}</span>
      </NuxtLink>

      <nav class="tc-nav" aria-label="Main">
        <NuxtLink v-for="l in links" :key="l.to" :to="l.to" class="tc-nav-link" :class="{ active: isActive(l) }">
          {{ l.label }}
        </NuxtLink>
      </nav>

      <div class="tc-user">
        <span class="tc-user-name">{{ userName }}</span>
        <button class="tc-signout" @click="$emit('signout')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          <span>Sign out</span>
        </button>
      </div>

      <button class="tc-burger" :aria-expanded="menuOpen" aria-label="Menu" @click="menuOpen = !menuOpen">
        <svg v-if="!menuOpen" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
        <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 5l14 14M19 5L5 19"/></svg>
      </button>
    </div>

    <!-- Mobile menu -->
    <div v-if="menuOpen" class="tc-mobile">
      <NuxtLink v-for="l in links" :key="l.to" :to="l.to" class="tc-mobile-link" :class="{ active: isActive(l) }" @click="menuOpen = false">
        {{ l.label }}
      </NuxtLink>
      <div class="tc-mobile-user">
        <span>{{ userName }}</span>
        <button class="tc-signout" @click="$emit('signout')">Sign out</button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  links:     { type: Array,  required: true },   // [{ to, label, match?, exact? }]
  homeTo:    { type: String, default: '/' },
  userName:  { type: String, default: '' },
  roleLabel: { type: String, default: '' },
})
defineEmits(['signout'])

const route = useRoute()
const menuOpen = ref(false)
watch(() => route.path, () => { menuOpen.value = false })

function isActive(l) {
  const prefix = l.match || l.to
  return l.exact ? route.path === prefix : route.path.startsWith(prefix)
}
</script>

<style scoped>
.tc-topbar {
  background: var(--brand-500);
  position: sticky; top: 0; z-index: 50;
  box-shadow: 0 2px 8px rgba(255,81,0,0.25);
}
.tc-topbar-inner {
  max-width: 1200px; margin: 0 auto; height: var(--topbar-h);
  padding: 0 1.5rem;
  display: flex; align-items: center; gap: 1.5rem;
}
.tc-brand { display: flex; align-items: center; gap: 0.75rem; text-decoration: none; }
.tc-brand-logo { height: 26px; width: auto; display: block; }
.tc-role {
  font-size: 0.66rem; font-weight: 700; letter-spacing: 1.1px; text-transform: uppercase;
  color: white; background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.35);
  padding: 0.2rem 0.55rem; border-radius: 50px; white-space: nowrap;
}

.tc-nav { display: flex; align-items: center; gap: 0.25rem; margin-left: auto; }
.tc-nav-link {
  color: rgba(255,255,255,0.85); text-decoration: none; font-size: 0.9rem; font-weight: 500;
  padding: 0.45rem 0.85rem; border-radius: 8px; transition: all 0.15s; white-space: nowrap;
}
.tc-nav-link:hover { background: rgba(255,255,255,0.14); color: white; }
.tc-nav-link.active { background: rgba(255,255,255,0.22); color: white; }

.tc-user { display: flex; align-items: center; gap: 0.9rem; }
.tc-user-name { color: rgba(255,255,255,0.92); font-size: 0.875rem; font-weight: 500; white-space: nowrap; max-width: 220px; overflow: hidden; text-overflow: ellipsis; }
.tc-signout {
  display: inline-flex; align-items: center; gap: 0.4rem;
  background: rgba(255,255,255,0.14); color: white; border: 1px solid rgba(255,255,255,0.35);
  padding: 0.42rem 0.8rem; border-radius: 8px; font-size: 0.82rem; font-weight: 500; cursor: pointer; transition: all 0.15s;
}
.tc-signout:hover { background: white; color: var(--brand-600); border-color: white; }

.tc-burger { display: none; margin-left: auto; background: none; border: none; color: white; cursor: pointer; padding: 0.35rem; }

.tc-mobile {
  display: none; flex-direction: column; gap: 0.25rem;
  padding: 0.75rem 1rem 1rem; background: var(--brand-600); border-top: 1px solid rgba(255,255,255,0.15);
}
.tc-mobile-link { color: white; text-decoration: none; font-weight: 500; padding: 0.7rem 0.75rem; border-radius: 8px; }
.tc-mobile-link.active, .tc-mobile-link:hover { background: rgba(255,255,255,0.16); }
.tc-mobile-user { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.75rem 0.75rem 0; margin-top: 0.5rem; border-top: 1px solid rgba(255,255,255,0.2); color: rgba(255,255,255,0.9); font-size: 0.875rem; }

@media (max-width: 820px) {
  .tc-topbar-inner { padding: 0 1rem; gap: 0.75rem; }
  .tc-nav, .tc-user { display: none; }
  .tc-burger { display: inline-flex; }
  .tc-mobile { display: flex; }
}
</style>
