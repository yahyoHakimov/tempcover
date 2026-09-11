<template>
  <div>

    <AppBreadcrumb :items="[{ label: 'Policies' }]" />

    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">All Policies</h1>
        <p class="page-sub">
          <span v-if="!selectedAgent && !viewAll">Select an agent to view their policies</span>
          <span v-else>
            Showing policies for <strong>{{ viewAll ? 'All Agents' : selectedAgent.name }}</strong>
            <button class="back-btn" @click="clearAgent">← Back to Agents</button>
          </span>
        </p>
      </div>
      <NuxtLink to="/superadmin/policies/create" class="btn-add">
        + Create Policy
      </NuxtLink>
    </div>

    <!-- AGENT CARDS VIEW -->
    <div v-if="!selectedAgent && !viewAll">

      <div v-if="loadingAgents" class="loading">Loading agents...</div>

      <div v-else-if="agents.length === 0" class="empty-state">
        <p class="empty-icon">👥</p>
        <p class="empty-text">No agents found</p>
      </div>

      <div v-else class="agents-grid">
        <button class="agent-card" @click="selectAll">
          <div class="agent-avatar">All</div>
          <div class="agent-info">
            <p class="agent-name">All Agents</p>
            <p class="agent-email">View policies across every agent</p>
          </div>
          <div class="arrow">→</div>
        </button>
        <button
          v-for="agent in agents"
          :key="agent.id"
          class="agent-card"
          @click="selectAgent(agent)"
        >
          <div class="agent-avatar">{{ initials(agent.name) }}</div>
          <div class="agent-info">
            <p class="agent-name">{{ agent.name }}</p>
            <p class="agent-username">@{{ agent.username }}</p>
            <p class="agent-email">{{ agent.email }}</p>
          </div>
          <div class="agent-meta">
            <span class="badge" :class="'badge-' + agent.status">{{ agent.status }}</span>
          </div>
          <div class="arrow">→</div>
        </button>
      </div>
    </div>

    <!-- POLICIES VIEW -->
    <div v-else>

      <div class="filters">
        <select v-model="filterStatus" @change="loadPolicies" class="filter-select">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="expired">Expired</option>
          <option value="cancelled">Cancelled</option>
          <option value="pending">Pending</option>
        </select>
        <div class="filter-count">{{ policies.length }} policies</div>
      </div>

      <div v-if="loadingPolicies" class="loading">Loading policies...</div>

      <div v-else-if="policies.length === 0" class="empty-state">
        <p class="empty-icon">📄</p>
        <p class="empty-text">No policies found</p>
      </div>

      <div v-else class="policies-grid">
        <div v-for="p in policies" :key="p.id" class="policy-card">
          <div class="policy-card-top">
            <div class="policy-reg">{{ p.policy_number }}</div>
            <span class="g-badge" :class="'g-badge-' + p.status">{{ p.status }}</span>
          </div>
          <div class="policy-card-body">
            <div class="policy-row" v-if="viewAll">
              <span class="policy-label">Agent</span>
              <span class="policy-value">{{ p.agent?.name || '—' }}</span>
            </div>
            <div class="policy-row">
              <span class="policy-label">Driver</span>
              <span class="policy-value">{{ p.driver ? p.driver.first_name + ' ' + p.driver.last_name : '—' }}</span>
            </div>
            <div class="policy-row">
              <span class="policy-label">Vehicle</span>
              <span class="policy-value">{{ p.vehicle ? p.vehicle.make + ' ' + p.vehicle.model : '—' }}</span>
            </div>
            <div class="policy-row">
              <span class="policy-label">From</span>
              <span class="policy-value">{{ formatDate(p.start_datetime) }}</span>
            </div>
            <div class="policy-row">
              <span class="policy-label">To</span>
              <span class="policy-value">{{ formatDate(p.end_datetime) }}</span>
            </div>
            <div class="policy-row">
              <span class="policy-label">Price</span>
              <span class="policy-value price">£{{ p.price.toFixed(2) }}</span>
            </div>
          </div>
          <div class="policy-card-actions">
            <NuxtLink :to="`/superadmin/policies/${p.id}`" class="g-btn g-btn-secondary" style="flex:1;justify-content:center;font-size:0.8rem;">View</NuxtLink>
            <button v-if="p.status === 'active'" class="g-btn g-btn-danger" style="flex:1;justify-content:center;font-size:0.8rem;" @click="cancelPolicy(p.id)">Cancel</button>
            <button class="g-btn g-btn-danger" style="flex:1;justify-content:center;font-size:0.8rem;" @click="deletePolicy(p)">Delete</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'

definePageMeta({ layout: 'superadmin' })

const auth = useAuthStore()
auth.init()

const route = useRoute()

const agents         = ref([])
const loadingAgents  = ref(true)
const selectedAgent  = ref(null)
const policies       = ref([])
const loadingPolicies = ref(false)
const filterStatus   = ref(
  ['active', 'expired', 'cancelled', 'pending'].includes(route.query.status) ? route.query.status : ''
)
const viewAll        = ref(route.query.view === 'all' || !!filterStatus.value)

onMounted(async () => {
  if (viewAll.value) loadPolicies()
  try {
    agents.value = await api.get('/api/superadmin/tenants', auth.token)
  } catch (e) {
    console.error(e)
  } finally {
    loadingAgents.value = false
  }
})

function selectAgent(agent) {
  selectedAgent.value = agent
  loadPolicies()
}

function selectAll() {
  viewAll.value = true
  loadPolicies()
}

function clearAgent() {
  selectedAgent.value = null
  viewAll.value = false
  policies.value = []
  filterStatus.value = ''
}

async function loadPolicies() {
  if (!selectedAgent.value && !viewAll.value) return
  loadingPolicies.value = true
  try {
    const params = []
    if (selectedAgent.value) params.push(`tenant_id=${selectedAgent.value.id}`)
    if (filterStatus.value) params.push(`status=${filterStatus.value}`)
    let url = '/api/superadmin/policies'
    if (params.length) url += '?' + params.join('&')
    policies.value = await api.get(url, auth.token)
  } catch (e) {
    console.error(e)
  } finally {
    loadingPolicies.value = false
  }
}

async function cancelPolicy(id) {
  if (!confirm('Cancel this policy?')) return
  try {
    await api.delete(`/api/superadmin/policies/${id}`, auth.token)
    await loadPolicies()
  } catch (e) {
    console.error(e)
  }
}

async function deletePolicy(p) {
  if (!confirm(`Permanently delete policy ${p.policy_number}? This cannot be undone.`)) return
  try {
    await api.delete(`/api/superadmin/policies/${p.id}/permanent`, auth.token)
    await loadPolicies()
  } catch (e) {
    console.error(e)
  }
}

function initials(name) {
  return name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || '?'
}

function formatDate(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}
.page-title { font-size: 1.6rem; font-weight: 700; color: var(--text-primary); }
.page-sub { color: #888; font-size: 0.9rem; margin-top: 0.25rem; }

.back-btn {
  margin-left: 0.75rem;
  background: none;
  border: none;
  color: var(--accent);
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
  padding: 0;
}
.back-btn:hover { text-decoration: underline; }

.btn-add {
  padding: 0.65rem 1.25rem;
  background: var(--accent);
  color: white;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  transition: background 0.2s;
}
.btn-add:hover { background: var(--brand-400); }

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
}

.agent-card {
  background: white;
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  border: 2px solid transparent;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
  width: 100%;
}
.agent-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(232,85,32,0.12);
}

.agent-avatar {
  width: 46px; height: 46px;
  background: var(--brand-500);
  color: white;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1rem;
  flex-shrink: 0;
}

.agent-info { flex: 1; min-width: 0; }
.agent-name     { font-weight: 700; color: var(--text-primary); font-size: 0.95rem; }
.agent-username { font-size: 0.78rem; color: var(--brand-700); font-weight: 600; margin-top: 1px; }
.agent-email    { font-size: 0.78rem; color: #888; margin-top: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.agent-meta { flex-shrink: 0; }
.arrow { color: #ccc; font-size: 1.1rem; flex-shrink: 0; }

.filters {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1.5rem;
}
.filter-select {
  padding: 0.6rem 1rem;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  font-size: 0.88rem;
  outline: none;
  background: white;
  cursor: pointer;
}
.filter-select:focus { border-color: var(--brand-700); }
.filter-count { margin-left: auto; font-size: 0.85rem; color: #888; }

.loading { text-align: center; padding: 3rem; color: #888; }

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 16px;
}
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-text { color: #888; }

.table-wrap {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  overflow-x: auto;
}
.table { width: 100%; border-collapse: collapse; min-width: 800px; }
.table th {
  background: var(--brand-50);
  padding: 0.85rem 1rem;
  text-align: left;
  font-size: 0.78rem;
  font-weight: 700;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid #eee;
}
.table td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid #f5f5f5;
  font-size: 0.85rem;
  color: #333;
  vertical-align: middle;
}
.table tr:last-child td { border-bottom: none; }
.table tr:hover td { background: #fafafa; }

.policy-num {
  background: var(--brand-50); color: var(--brand-700);
  padding: 0.2rem 0.5rem; border-radius: 6px;
  font-size: 0.8rem; font-weight: 600;
}
.name { font-weight: 600; color: var(--text-primary); font-size: 0.85rem; }
.name.reg {
  font-family: monospace;
  background: #f5f5f5;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  letter-spacing: 1px;
}
.sub   { font-size: 0.75rem; color: #888; margin-top: 2px; }
.date  { font-size: 0.82rem; color: #333; }
.price { font-weight: 700; color: var(--text-primary); }
.text-gray { color: #aaa; font-size: 0.82rem; }

.badge {
  padding: 0.25rem 0.65rem;
  border-radius: 50px;
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: capitalize;
}
.badge-active    { background: #e6f9f0; color: #00873a; }
.badge-expired   { background: #f5f5f5; color: #888; }
.badge-cancelled { background: #fff0f0; color: #cc0000; }
.badge-pending   { background: #fff8e6; color: #b36b00; }
.badge-suspended { background: #fff0f0; color: #cc0000; }

.actions { display: flex; gap: 0.5rem; }
.btn-sm {
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  text-decoration: none;
  display: inline-block;
  transition: all 0.2s;
}
.btn-view   { background: var(--brand-50); color: var(--brand-700); }
.btn-view:hover { background: var(--brand-100); }
.btn-cancel { background: #fff0f0; color: #cc0000; }
.btn-cancel:hover { background: #ffdddd; }
.policies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.policy-card {
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
.policy-card:hover {
  border-color: var(--brand-300);
  box-shadow: 0 4px 20px rgba(255,81,0,0.1);
}

.policy-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.policy-reg {
  font-family: monospace;
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--brand-800);
  letter-spacing: 1px;
  background: var(--brand-50);
  padding: 0.3rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--brand-200);
}

.policy-card-body {
  background: var(--brand-50);
  border-radius: 10px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.policy-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
}
.policy-label { color: var(--text-muted); font-weight: 500; }
.policy-value { font-weight: 600; color: var(--text-primary); }
.policy-value.price { color: var(--brand-700); font-size: 0.95rem; }

.policy-card-actions {
  display: flex;
  gap: 0.5rem;
}

@media (max-width: 640px) {
  .policies-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  /* Header */
  .page-header { flex-direction: column; gap: 1rem; }
  .btn-add { width: 100%; text-align: center; }

  /* Agent cards */
  .agents-grid { grid-template-columns: 1fr; }
  .agent-card { padding: 1rem; }
  .agent-email { display: none; }

  /* Filters */
  .filters { flex-wrap: wrap; }
  .filter-select { width: 100%; }
  .filter-count { width: 100%; text-align: right; }

  /* Table — horizontal scroll */
  .table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .table { min-width: 650px; }
  .table th, .table td { padding: 0.65rem 0.75rem; font-size: 0.78rem; }
}

@media (max-width: 480px) {
  /* Agent card — compact */
  .agent-card { gap: 0.75rem; }
  .agent-avatar { width: 38px; height: 38px; font-size: 0.85rem; }
  .agent-name { font-size: 0.88rem; }
  .agent-username { font-size: 0.72rem; }
  .arrow { display: none; }

  /* Page title */
  .page-title { font-size: 1.3rem; }
  .page-sub { font-size: 0.82rem; }

  /* Table columns — hide less important ones on very small screens */
  .table th:nth-child(3),
  .table td:nth-child(3) { display: none; }
}
</style>