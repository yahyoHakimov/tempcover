<template>
  <div class="dash">

    <!-- Session countdown -->
    <section class="dash-card session-card">
      <h2 class="session-title">Session Expires In</h2>
      <AdminCountdown :expires-at="expiresAt" />
    </section>

    <!-- Primary action -->
    <section class="dash-card action-card">
      <NuxtLink to="/admin/policies/create" class="create-btn">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        <span>Create Policy</span>
      </NuxtLink>
    </section>

    <!-- Navigation cards -->
    <NuxtLink to="/admin/policies" class="dash-card link-card">
      <span class="link-icon icon-solid">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
      </span>
      <span class="link-text">
        <span class="link-title">Created Policies</span>
        <span class="link-desc">View all created policies</span>
      </span>
      <span v-if="counts.total !== null" class="link-count">{{ counts.total }}</span>
      <svg class="link-chevron" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
    </NuxtLink>

    <NuxtLink to="/admin/policies?filter=expiring3" class="dash-card link-card">
      <span class="link-icon icon-orange">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      </span>
      <span class="link-text">
        <span class="link-title">Expiring within 3 days</span>
        <span class="link-desc">Urgent renewals needed</span>
      </span>
      <span v-if="counts.expiring3 !== null" class="link-count" :class="{ hot: counts.expiring3 > 0 }">{{ counts.expiring3 }}</span>
      <svg class="link-chevron" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
    </NuxtLink>

    <NuxtLink to="/admin/policies?filter=expiringweek" class="dash-card link-card">
      <span class="link-icon icon-yellow">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
      </span>
      <span class="link-text">
        <span class="link-title">Expiring this week</span>
        <span class="link-desc">Weekly renewal overview</span>
      </span>
      <span v-if="counts.expiringweek !== null" class="link-count">{{ counts.expiringweek }}</span>
      <svg class="link-chevron" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
    </NuxtLink>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'

definePageMeta({ layout: 'admin' })
useHead({ title: 'Dashboard' })

const auth = useAuthStore()
auth.init()

const expiresAt = ref(null)
const counts = ref({ total: null, expiring3: null, expiringweek: null })

onMounted(async () => {
  try {
    const me = await api.get('/api/auth/me', auth.token)
    expiresAt.value = me.user?.expires_at || null
  } catch (e) { console.error(e) }

  try {
    const [all, e3, ew] = await Promise.all([
      api.get('/api/policies/', auth.token),
      api.get('/api/policies/?filter=expiring3', auth.token),
      api.get('/api/policies/?filter=expiringweek', auth.token),
    ])
    counts.value = { total: all.length, expiring3: e3.length, expiringweek: ew.length }
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.dash { display: flex; flex-direction: column; gap: 2rem; }

.dash-card {
  background: var(--card-bg); border: 1px solid var(--card-border); border-radius: var(--card-radius);
  box-shadow: var(--card-shadow);
}

/* Session */
.session-card { padding: 1.9rem 1.5rem 2.1rem; }
.session-title { font-size: 1.2rem; font-weight: 500; color: var(--text-primary); text-align: center; margin-bottom: 1.5rem; }

/* Create policy */
.action-card { padding: 1.5rem; }
.create-btn {
  display: flex; align-items: center; justify-content: center; gap: 0.75rem;
  width: 100%; height: 68px;
  background: var(--brand-500); color: white; border-radius: 10px;
  font-size: 1.2rem; font-weight: 500; text-decoration: none;
  transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
}
.create-btn:hover { background: var(--brand-600); transform: translateY(-1px); box-shadow: 0 8px 22px rgba(255,81,0,0.30); }
.create-btn:active { transform: translateY(0); }

/* Link cards */
.link-card {
  display: flex; align-items: center; gap: 1.2rem;
  padding: 1.5rem; text-decoration: none; color: inherit;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}
.link-card:hover { border-color: var(--brand-300); box-shadow: var(--card-shadow-hover); transform: translateY(-2px); }
.link-card:hover .link-chevron { color: var(--brand-500); transform: translateX(3px); }

.link-icon { width: 52px; height: 52px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.icon-solid  { background: var(--brand-500); color: white; }
.icon-orange { background: var(--brand-100); color: var(--brand-500); }
.icon-yellow { background: #FFF6DB; color: #E0A100; }

.link-text { display: flex; flex-direction: column; gap: 0.3rem; min-width: 0; flex: 1; }
.link-title { font-size: 1.15rem; font-weight: 500; color: var(--text-primary); }
.link-desc { font-size: 0.9rem; color: var(--text-muted); }

.link-count {
  min-width: 34px; height: 34px; padding: 0 0.7rem; border-radius: 50px;
  background: var(--gray-100); color: var(--text-secondary);
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 0.9rem; font-weight: 700; font-variant-numeric: tabular-nums;
}
.link-count.hot { background: var(--brand-100); color: var(--brand-600); }
.link-chevron { color: var(--gray-400); flex-shrink: 0; transition: color 0.2s, transform 0.2s; }

@media (max-width: 640px) {
  .dash { gap: 1.25rem; }
  .session-card { padding: 1.5rem 1rem 1.6rem; }
  .action-card { padding: 1rem; }
  .create-btn { height: 58px; font-size: 1.05rem; }
  .link-card { padding: 1.1rem 1rem; gap: 0.9rem; }
  .link-icon { width: 46px; height: 46px; }
  .link-title { font-size: 1.02rem; }
  .link-desc { font-size: 0.82rem; }
}
</style>
