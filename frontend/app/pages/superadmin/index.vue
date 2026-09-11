<template>
  <div>
    <div class="g-header">
      <div>
        <h1 class="g-title">Dashboard</h1>
        <p class="g-subtitle">Welcome back, {{ auth.name }}</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="g-stats">
      <NuxtLink to="/superadmin/tenants" class="g-stat">
        <div class="g-stat-icon" style="background:#FFEDE3;">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#FF5100" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div>
          <p class="g-stat-label">Total Agents</p>
          <p class="g-stat-value">{{ stats.total_tenants ?? '—' }}</p>
        </div>
      </NuxtLink>
      <NuxtLink to="/superadmin/tenants?status=active" class="g-stat">
        <div class="g-stat-icon" style="background:#ecfdf5;">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <div>
          <p class="g-stat-label">Active Agents</p>
          <p class="g-stat-value">{{ stats.active_tenants ?? '—' }}</p>
        </div>
      </NuxtLink>
      <NuxtLink to="/superadmin/policies?view=all" class="g-stat">
        <div class="g-stat-icon" style="background:#fffbeb;">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </div>
        <div>
          <p class="g-stat-label">Total Policies</p>
          <p class="g-stat-value">{{ stats.total_policies ?? '—' }}</p>
        </div>
      </NuxtLink>
      <NuxtLink to="/superadmin/policies?status=active" class="g-stat">
        <div class="g-stat-icon" style="background:#eff6ff;">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>
        </div>
        <div>
          <p class="g-stat-label">Active Policies</p>
          <p class="g-stat-value">{{ stats.active_policies ?? '—' }}</p>
        </div>
      </NuxtLink>
    </div>

    <!-- Quick Actions -->
    <div class="section-title">Quick Actions</div>
    <div class="actions-grid">
      <NuxtLink to="/superadmin/policies/create" class="action-card action-primary">
        <div class="action-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
        </div>
        <span class="action-label">Create Policy</span>
        <span class="action-desc">Issue a new policy</span>
      </NuxtLink>
      <NuxtLink to="/superadmin/tenants/create" class="action-card">
        <div class="action-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/></svg>
        </div>
        <span class="action-label">Add Agent</span>
        <span class="action-desc">Create new agent</span>
      </NuxtLink>
      <NuxtLink to="/superadmin/tenants" class="action-card">
        <div class="action-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <span class="action-label">Manage Agents</span>
        <span class="action-desc">View all agents</span>
      </NuxtLink>
      <NuxtLink to="/superadmin/policies" class="action-card">
        <div class="action-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </div>
        <span class="action-label">All Policies</span>
        <span class="action-desc">View all policies</span>
      </NuxtLink>
      <NuxtLink to="/superadmin/drivers" class="action-card">
        <div class="action-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/><line x1="12" y1="2" x2="12" y2="9"/><line x1="12" y1="15" x2="12" y2="22"/><line x1="2" y1="12" x2="9" y2="12"/><line x1="15" y1="12" x2="22" y2="12"/></svg>
        </div>
        <span class="action-label">Drivers</span>
        <span class="action-desc">View &amp; manage drivers</span>
      </NuxtLink>
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
const stats = ref({})

onMounted(async () => {
  try {
    stats.value = await api.get('/api/superadmin/dashboard', auth.token)
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.section-title {
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.action-card {
  background: var(--card-bg);
  border-radius: var(--card-radius);
  padding: 1.5rem 1.25rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
  text-decoration: none;
  box-shadow: var(--card-shadow);
  border: 1.5px solid transparent;
  transition: all 0.18s;
  color: var(--text-primary);
}
.action-card:hover {
  border-color: var(--brand-400);
  box-shadow: 0 4px 20px rgba(255,81,0,0.1);
  transform: translateY(-2px);
}

.action-primary {
  background: var(--brand-500);
  border-color: transparent;
  color: white;
}
.action-primary .action-label { color: white; }
.action-primary .action-desc  { color: rgba(255,255,255,0.7); }
.action-primary .action-icon  { color: white; opacity: 0.9; }

.action-icon {
  color: var(--brand-500);
  display: flex;
  align-items: center;
  margin-bottom: 0.25rem;
}

.action-label {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-primary);
}

.action-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .actions-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 480px) {
  .actions-grid { grid-template-columns: 1fr 1fr; gap: 0.75rem; }
}
</style>