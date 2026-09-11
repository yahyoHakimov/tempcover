<template>
  <div>
    <div class="g-header">
      <div>
        <h1 class="g-title">Agents</h1>
        <p class="g-subtitle">Manage all agents on the platform</p>
      </div>
      <NuxtLink to="/superadmin/tenants/create" class="g-btn g-btn-primary">+ Add Agent</NuxtLink>
    </div>

    <div class="g-filters">
      <select v-model="statusFilter" @change="onFilterChange" class="g-filter-select">
        <option value="">All Agents</option>
        <option value="active">Active</option>
        <option value="suspended">Suspended</option>
      </select>
      <span style="margin-left:auto;font-size:0.82rem;color:var(--text-muted);">{{ filteredTenants.length }} agents</span>
    </div>

    <div v-if="loading" class="g-loading">Loading...</div>

    <div v-else-if="filteredTenants.length === 0" class="g-empty">
      <div class="g-empty-icon">👥</div>
      <p class="g-empty-text">No agents found</p>
    </div>

    <div v-else class="agents-grid">
      <div v-for="t in filteredTenants" :key="t.id" class="agent-card">

        <!-- Top -->
        <div class="card-top">
          <div class="agent-avatar">{{ initials(t.name) }}</div>
          <div class="agent-info">
            <p class="agent-name">{{ t.name }}</p>
            <p class="agent-email">{{ t.email }}</p>
            <code class="agent-username">@{{ t.username }}</code>
          </div>
          <span class="g-badge" :class="'g-badge-' + t.status">{{ t.status }}</span>
        </div>

        <!-- Details -->
        <div class="card-details">
          <div class="detail-row">
            <span class="detail-label">Plan</span>
            <span class="detail-value">{{ t.plan }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Monthly Fee</span>
            <span class="detail-value">£{{ t.monthly_fee }}/mo</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Expires</span>
            <span class="detail-value" v-if="t.expires_at"
              :style="isExpired(t.expires_at) ? 'color:var(--error)' : 'color:var(--success)'">
              {{ formatDate(t.expires_at) }}
            </span>
            <span class="detail-value" v-else style="color:var(--text-muted)">No expiry</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="card-actions">
          <NuxtLink :to="`/superadmin/tenants/${t.id}`" class="g-btn g-btn-secondary" style="flex:1;justify-content:center;">
            Edit
          </NuxtLink>
          <button
            v-if="t.status === 'active'"
            class="g-btn g-btn-danger"
            style="flex:1;justify-content:center;"
            @click="suspend(t.id)"
          >Suspend</button>
          <button
            v-else
            class="g-btn"
            style="flex:1;justify-content:center;background:var(--success-bg);color:var(--success);border:1px solid var(--success-border);"
            @click="activate(t.id)"
          >Activate</button>
        </div>

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
const tenants = ref([])
const loading = ref(true)

const route = useRoute()
const router = useRouter()
const statusFilter = ref(['active', 'suspended'].includes(route.query.status) ? route.query.status : '')

const filteredTenants = computed(() =>
  statusFilter.value ? tenants.value.filter(t => t.status === statusFilter.value) : tenants.value
)

function onFilterChange() {
  router.replace({ query: statusFilter.value ? { status: statusFilter.value } : {} })
}

async function load() {
  try { tenants.value = await api.get('/api/superadmin/tenants', auth.token) }
  catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function suspend(id) {
  if (!confirm('Suspend this agent?')) return
  await api.post(`/api/superadmin/tenants/${id}/suspend`, {}, auth.token)
  await load()
}

async function activate(id) {
  await api.post(`/api/superadmin/tenants/${id}/activate`, {}, auth.token)
  await load()
}

function initials(name) {
  return name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || '?'
}
function formatDate(dt) {
  return new Date(dt).toLocaleDateString('en-GB', { day:'2-digit', month:'short', year:'numeric' })
}
function isExpired(dt) { return new Date(dt) < new Date() }

onMounted(load)
</script>

<style scoped>
.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.agent-card {
  background: white;
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: var(--card-shadow);
  border: 1px solid rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: all 0.18s;
}
.agent-card:hover {
  border-color: var(--brand-300);
  box-shadow: 0 4px 20px rgba(255,81,0,0.1);
}

.card-top {
  display: flex;
  align-items: flex-start;
  gap: 0.875rem;
}

.agent-avatar {
  width: 44px; height: 44px;
  background: var(--brand-500);
  color: white;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.95rem;
  flex-shrink: 0;
}

.agent-info { flex: 1; min-width: 0; }
.agent-name  { font-weight: 700; color: var(--text-primary); font-size: 0.95rem; }
.agent-email { font-size: 0.75rem; color: var(--text-muted); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.agent-username { font-size: 0.72rem; color: var(--brand-600); font-weight: 600; margin-top: 3px; display: block; }

.card-details {
  background: var(--brand-50);
  border-radius: 10px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
}
.detail-label { color: var(--text-muted); font-weight: 500; }
.detail-value { font-weight: 600; color: var(--text-primary); text-transform: capitalize; }

.card-actions {
  display: flex;
  gap: 0.5rem;
}

@media (max-width: 640px) {
  .agents-grid { grid-template-columns: 1fr; }
  .g-header { flex-direction: column; gap: 0.75rem; }
  .g-header .g-btn { width: 100%; justify-content: center; text-align: center; }
}
</style>
