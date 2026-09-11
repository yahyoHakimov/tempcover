<template>
  <div>
    <div class="g-header">
      <div>
        <h1 class="g-title">Drivers</h1>
        <p class="g-subtitle">{{ drivers.length }} driver{{ drivers.length === 1 ? '' : 's' }} across all agents</p>
      </div>
      <NuxtLink to="/superadmin/policies/create" class="g-btn g-btn-primary">+ Create Policy</NuxtLink>
    </div>

    <div v-if="toast.show" class="g-toast" :class="toast.type">{{ toast.message }}</div>

    <!-- Search + filters -->
    <div class="toolbar">
      <input v-model="query" type="text" class="g-input search" placeholder="Search by name, email, licence or agent..." />
      <div class="chips">
        <button class="chip" :class="{ on: filter === 'all' }" @click="filter = 'all'">All ({{ drivers.length }})</button>
        <button class="chip chip-green" :class="{ on: filter === 'active' }" @click="filter = 'active'">Active policy ({{ counts.active }})</button>
        <button class="chip chip-brand" :class="{ on: filter === 'with' }" @click="filter = 'with'">Has policies ({{ counts.with_ }})</button>
        <button class="chip chip-gray" :class="{ on: filter === 'none' }" @click="filter = 'none'">No policies ({{ counts.none }})</button>
      </div>
    </div>

    <div v-if="loading" class="g-loading">Loading...</div>

    <div v-else-if="filtered.length === 0" class="g-empty">
      <div class="g-empty-icon">🚗</div>
      <p class="g-empty-text">{{ drivers.length === 0 ? 'No drivers yet' : 'No drivers match your search' }}</p>
    </div>

    <div v-else class="drivers-grid">
      <div
        v-for="d in filtered"
        :key="d.id"
        class="driver-card"
        :class="cardClass(d)"
      >
        <div class="card-top">
          <div class="driver-id">
            <div class="avatar">{{ initials(d) }}</div>
            <div class="name-wrap">
              <p class="driver-name">{{ d.first_name }} {{ d.last_name }}</p>
              <p class="driver-city">{{ d.city }}</p>
            </div>
          </div>
          <span v-if="d.active_policy_count > 0" class="g-badge g-badge-active">Active</span>
          <span v-else-if="d.policy_count > 0" class="g-badge badge-had">{{ d.policy_count }} {{ d.policy_count === 1 ? 'policy' : 'policies' }}</span>
          <span v-else class="g-badge badge-none">No policies</span>
        </div>

        <div class="card-body">
          <div class="card-row"><span class="card-label">Agent</span><span class="card-value ellip">{{ d.agent_name }}</span></div>
          <div class="card-row"><span class="card-label">Email</span><span class="card-value ellip">{{ d.email }}</span></div>
          <div class="card-row"><span class="card-label">Mobile</span><span class="card-value">{{ d.mobile }}</span></div>
          <div class="card-row"><span class="card-label">Policies</span><span class="card-value">{{ d.policy_count }}</span></div>
          <div class="card-row">
            <span class="card-label">Last policy</span>
            <span class="card-value" :class="{ never: !d.last_policy_at }">{{ fmtDate(d.last_policy_at) }}</span>
          </div>
        </div>

        <button class="g-btn g-btn-danger del-btn" @click="deleteDriver(d)" :disabled="deletingId === d.id">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
          {{ deletingId === d.id ? 'Deleting...' : 'Delete Driver' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'

definePageMeta({ layout: 'superadmin' })
const auth = useAuthStore()
auth.init()

const drivers = ref([])
const loading = ref(true)
const query = ref('')
const filter = ref('all')
const deletingId = ref(null)
const toast = ref({ show: false, message: '', type: 'success' })

function showToast(msg, type='success') {
  toast.value = { show:true, message:msg, type }
  setTimeout(() => toast.value.show = false, 4000)
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
    (d.driving_licence || '').toLowerCase().includes(q) ||
    (d.agent_name || '').toLowerCase().includes(q)
  )
})

function initials(d) {
  return `${(d.first_name || '?')[0]}${(d.last_name || '?')[0]}`.toUpperCase()
}

function cardClass(d) {
  if (d.active_policy_count > 0) return 'is-active'
  if (d.policy_count > 0) return 'is-had'
  return 'is-none'
}

function fmtDate(s) {
  if (!s) return 'Never'
  return new Date(s).toLocaleDateString('en-GB', { day:'2-digit', month:'short', year:'numeric' })
}

async function deleteDriver(d) {
  if (!confirm(`Delete driver ${d.first_name} ${d.last_name}? Their old (cancelled/expired) policy records will also be removed. This cannot be undone.`)) return
  deletingId.value = d.id
  try {
    await api.delete(`/api/superadmin/drivers/${d.id}`, auth.token)
    drivers.value = drivers.value.filter(x => x.id !== d.id)
    showToast('Driver deleted!')
  } catch(e) { showToast(e.message, 'error') }
  finally { deletingId.value = null }
}

onMounted(async () => {
  try {
    drivers.value = await api.get('/api/superadmin/drivers', auth.token)
  } catch(e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<style scoped>
.toolbar { display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; }
.search { max-width: 320px; }

.chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.chip {
  padding: 0.45rem 0.8rem;
  border-radius: 50px;
  border: 1.5px solid var(--gray-200);
  background: white;
  font-size: 0.78rem; font-weight: 600;
  color: var(--text-muted);
  cursor: pointer; transition: all 0.15s;
  font-family: var(--font);
}
.chip:hover { border-color: var(--brand-400); color: var(--brand-700); }
.chip.on { background: var(--brand-700); border-color: var(--brand-700); color: white; }
.chip-brand.on  { background: var(--brand-500); border-color: var(--brand-500); }
.chip-green.on  { background: #059669; border-color: #059669; }
.chip-gray.on   { background: #6b7280; border-color: #6b7280; }

.drivers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}

.driver-card {
  background: white;
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: var(--card-shadow);
  border: 1px solid rgba(0,0,0,0.04);
  border-left: 4px solid var(--gray-200);
  display: flex; flex-direction: column; gap: 1rem;
  transition: all 0.18s;
}
.driver-card:hover { box-shadow: 0 4px 20px rgba(255,81,0,0.1); }
.driver-card.is-active { border-left-color: #059669; }
.driver-card.is-had    { border-left-color: var(--brand-500); }
.driver-card.is-none   { border-left-color: var(--gray-200); }

.card-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 0.5rem; }

.driver-id { display: flex; align-items: center; gap: 0.7rem; min-width: 0; }
.avatar {
  width: 38px; height: 38px; flex-shrink: 0;
  background: var(--brand-500);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-weight: 700; font-size: 0.82rem;
}
.name-wrap { min-width: 0; }
.driver-name { font-size: 0.92rem; font-weight: 700; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.driver-city { font-size: 0.75rem; color: var(--text-muted); margin-top: 1px; }

.badge-had  { background: var(--brand-100, #FFEDE3); color: var(--brand-700); border: 1px solid var(--brand-200); }
.badge-none { background: var(--gray-100); color: var(--gray-500); border: 1px solid var(--gray-200); }

.card-body {
  background: var(--brand-50);
  border-radius: 10px;
  padding: 0.75rem;
  display: flex; flex-direction: column; gap: 0.4rem;
  flex: 1;
}
.card-row { display: flex; justify-content: space-between; align-items: center; gap: 0.75rem; font-size: 0.8rem; }
.card-label { color: var(--text-muted); font-weight: 500; flex-shrink: 0; }
.card-value { font-weight: 600; color: var(--text-primary); }
.card-value.ellip { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-value.never { color: var(--text-muted); font-weight: 500; }

.del-btn { width: 100%; justify-content: center; font-size: 0.82rem; gap: 0.4rem; }

@media (max-width: 640px) {
  .drivers-grid { grid-template-columns: 1fr; }
  .search { max-width: 100%; width: 100%; }
}
</style>
