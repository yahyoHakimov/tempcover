<template>
  <div>
    <div class="page-head">
      <div>
        <h1 class="g-title">Drivers</h1>
        <p class="g-subtitle">{{ drivers.length }} saved driver{{ drivers.length === 1 ? '' : 's' }}</p>
      </div>
      <NuxtLink to="/admin/policies/create" class="g-btn g-btn-primary">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Create Policy
      </NuxtLink>
    </div>

    <div v-if="toast.show" class="g-toast" :class="toast.type">{{ toast.message }}</div>

    <div class="toolbar">
      <div class="chips">
        <button class="chip" :class="{ on: filter === 'all' }" @click="filter = 'all'">All ({{ drivers.length }})</button>
        <button class="chip" :class="{ on: filter === 'active' }" @click="filter = 'active'">Active policy ({{ counts.active }})</button>
        <button class="chip" :class="{ on: filter === 'with' }" @click="filter = 'with'">Has policies ({{ counts.with_ }})</button>
        <button class="chip" :class="{ on: filter === 'none' }" @click="filter = 'none'">No policies ({{ counts.none }})</button>
      </div>
      <input v-model="query" type="search" class="g-input search" placeholder="Search by name, email or licence…" />
    </div>

    <div v-if="loading" class="g-loading">Loading drivers…</div>

    <div v-else-if="filtered.length === 0" class="g-empty">
      <div class="g-empty-icon">🚗</div>
      <p class="g-empty-text">{{ drivers.length === 0 ? 'No drivers yet — they are saved when you create a policy' : 'No drivers match your search' }}</p>
    </div>

    <div v-else class="drivers-grid">
      <div v-for="d in filtered" :key="d.id" class="driver-card" :class="cardClass(d)">
        <div class="card-top">
          <div class="driver-id">
            <div class="avatar">{{ initials(d) }}</div>
            <div class="name-wrap">
              <p class="driver-name">{{ d.first_name }} {{ d.last_name }}</p>
              <p class="driver-city">{{ d.city }}, {{ d.postcode }}</p>
            </div>
          </div>
          <span v-if="d.active_policy_count > 0" class="g-badge g-badge-active">Active</span>
          <span v-else-if="d.policy_count > 0" class="g-badge badge-had">{{ d.policy_count }} {{ d.policy_count === 1 ? 'policy' : 'policies' }}</span>
          <span v-else class="g-badge g-badge-expired">No policies</span>
        </div>

        <div class="card-body">
          <div class="card-row"><span class="card-label">Email</span><span class="card-value ellip">{{ d.email }}</span></div>
          <div class="card-row"><span class="card-label">Mobile</span><span class="card-value">{{ d.mobile }}</span></div>
          <div class="card-row"><span class="card-label">Licence</span><span class="card-value mono">{{ d.driving_licence }}</span></div>
          <div class="card-row"><span class="card-label">Policies</span><span class="card-value">{{ d.policy_count }}</span></div>
          <div class="card-row"><span class="card-label">Last policy</span><span class="card-value" :class="{ never: !d.last_policy_at }">{{ d.last_policy_at ? fmtDate(d.last_policy_at) : 'Never' }}</span></div>
        </div>

        <div class="card-actions">
          <NuxtLink :to="`/admin/policies?q=${encodeURIComponent(d.last_name)}`" class="g-btn g-btn-ghost small">View policies</NuxtLink>
          <button class="g-btn g-btn-danger small" @click="deleteDriver(d)" :disabled="deletingId === d.id">
            {{ deletingId === d.id ? 'Deleting…' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'
import { fmtDate } from '~/utils/format'

definePageMeta({ layout: 'admin' })
useHead({ title: 'Drivers' })

const auth = useAuthStore()
auth.init()

const drivers = ref([])
const loading = ref(true)
const query = ref('')
const filter = ref('all')
const deletingId = ref(null)
const toast = ref({ show: false, message: '', type: 'success' })

function showToast(msg, type = 'success') {
  toast.value = { show: true, message: msg, type }
  setTimeout(() => (toast.value.show = false), 4000)
}

const counts = computed(() => ({
  active: drivers.value.filter(d => d.active_policy_count > 0).length,
  with_:  drivers.value.filter(d => d.policy_count > 0).length,
  none:   drivers.value.filter(d => d.policy_count === 0).length,
}))

const filtered = computed(() => {
  let list = drivers.value
  if (filter.value === 'active') list = list.filter(d => d.active_policy_count > 0)
  if (filter.value === 'with')   list = list.filter(d => d.policy_count > 0)
  if (filter.value === 'none')   list = list.filter(d => d.policy_count === 0)
  const q = query.value.toLowerCase().trim()
  if (!q) return list
  return list.filter(d =>
    `${d.first_name} ${d.last_name}`.toLowerCase().includes(q) ||
    (d.email || '').toLowerCase().includes(q) ||
    (d.driving_licence || '').toLowerCase().includes(q)
  )
})

const initials = (d) => `${(d.first_name || '?')[0]}${(d.last_name || '?')[0]}`.toUpperCase()
const cardClass = (d) => d.active_policy_count > 0 ? 'is-active' : d.policy_count > 0 ? 'is-had' : 'is-none'

async function deleteDriver(d) {
  if (!confirm(`Delete driver ${d.first_name} ${d.last_name}? Their old (cancelled/expired) policy records will also be removed. This cannot be undone.`)) return
  deletingId.value = d.id
  try {
    await api.delete(`/api/drivers/${d.id}`, auth.token)
    drivers.value = drivers.value.filter(x => x.id !== d.id)
    showToast('Driver deleted')
  } catch (e) { showToast(e.message, 'error') }
  finally { deletingId.value = null }
}

onMounted(async () => {
  try { drivers.value = await api.get('/api/drivers/', auth.token) }
  catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.25rem; }
.chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.search { max-width: 320px; padding: 0.6rem 0.9rem; font-size: 0.875rem; }

.drivers-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 1rem; }

.driver-card {
  background: white; border-radius: var(--card-radius); padding: 1.25rem;
  box-shadow: var(--card-shadow); border: 1px solid var(--card-border); border-left: 4px solid var(--gray-200);
  display: flex; flex-direction: column; gap: 1rem; transition: all 0.18s;
}
.driver-card:hover { box-shadow: var(--card-shadow-hover); }
.driver-card.is-active { border-left-color: var(--success); }
.driver-card.is-had    { border-left-color: var(--brand-500); }

.card-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 0.5rem; }
.driver-id { display: flex; align-items: center; gap: 0.7rem; min-width: 0; }
.avatar {
  width: 40px; height: 40px; flex-shrink: 0; background: linear-gradient(135deg, var(--brand-600), var(--brand-400));
  border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 0.85rem;
}
.name-wrap { min-width: 0; }
.driver-name { font-size: 0.95rem; font-weight: 700; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.driver-city { font-size: 0.75rem; color: var(--text-muted); margin-top: 1px; }
.badge-had { background: var(--brand-50); color: var(--brand-700); border: 1px solid var(--brand-200); }

.card-body { background: var(--gray-50); border-radius: 10px; padding: 0.75rem; display: flex; flex-direction: column; gap: 0.4rem; flex: 1; }
.card-row { display: flex; justify-content: space-between; align-items: center; gap: 0.75rem; font-size: 0.8rem; }
.card-label { color: var(--text-muted); flex-shrink: 0; }
.card-value { font-weight: 500; color: var(--text-primary); }
.card-value.ellip { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-value.mono { font-family: 'Courier New', monospace; font-size: 0.78rem; }
.card-value.never { color: var(--text-muted); font-weight: 400; }

.card-actions { display: flex; gap: 0.5rem; }
.card-actions .g-btn { flex: 1; }
.small { font-size: 0.8rem; padding: 0.5rem 0.75rem; }

@media (max-width: 640px) {
  .page-head .g-btn { width: 100%; }
  .drivers-grid { grid-template-columns: 1fr; }
  .search { max-width: 100%; width: 100%; }
}
</style>
