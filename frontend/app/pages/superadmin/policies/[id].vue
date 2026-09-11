<template>
  <div>
    <AppBreadcrumb :items="breadcrumbs" />

    <div class="page-header">
      <div>
        <h1 class="page-title">Policy Detail</h1>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else-if="!data" class="empty-state">
      <p>Policy not found</p>
    </div>

    <div v-else class="detail-grid">

      <!-- Policy Info -->
      <div class="card">
        <h2 class="card-title">📄 Policy</h2>
        <div class="info-list">
          <div class="info-row">
            <span class="label">Policy Number</span>
            <code class="policy-num">{{ data.policy.policy_number }}</code>
          </div>
          <div class="info-row">
            <span class="label">Status</span>
            <span class="badge" :class="'badge-' + data.policy.status">{{ data.policy.status }}</span>
          </div>
          <div class="info-row">
            <span class="label">Cover Type</span>
            <span>{{ data.policy.cover_type }}</span>
          </div>
          <div class="info-row">
            <span class="label">Price</span>
            <span class="price">£{{ data.policy.price.toFixed(2) }}</span>
          </div>
          <div class="info-row">
            <span class="label">Start</span>
            <span>{{ formatDate(data.policy.start_datetime) }}</span>
          </div>
          <div class="info-row">
            <span class="label">End</span>
            <span>{{ formatDate(data.policy.end_datetime) }}</span>
          </div>
          <div class="info-row">
            <span class="label">Compulsory Excess</span>
            <span>£{{ data.policy.compulsory_excess }}</span>
          </div>
          <div class="info-row">
            <span class="label">Email Sent</span>
            <span>{{ data.policy.email_sent ? '✅ Yes' : '❌ No' }}</span>
          </div>
          <div class="info-row">
            <span class="label">Issued At</span>
            <span>{{ formatDate(data.policy.issued_at) }}</span>
          </div>
        </div>

        <!-- Edit button -->
        <NuxtLink
          :to="`/superadmin/policies/edit/${route.params.id}`"
          class="btn-edit"
        >
          Edit Policy
        </NuxtLink>

        <!-- Cancel button -->
        <button
          v-if="data.policy.status === 'active'"
          class="btn-cancel"
          @click="cancelPolicy"
        >
          Cancel Policy
        </button>

        <!-- Delete button -->
        <button class="btn-delete" @click="deletePolicy">
          Delete Policy
        </button>
      </div>

      <!-- Agent Info -->
      <div class="card" v-if="data.agent">
        <h2 class="card-title">🏢 Agent</h2>
        <div class="info-list">
          <div class="info-row">
            <span class="label">Name</span>
            <span>{{ data.agent.name }}</span>
          </div>
          <div class="info-row">
            <span class="label">Username</span>
            <code>{{ data.agent.username }}</code>
          </div>
          <div class="info-row">
            <span class="label">Email</span>
            <span>{{ data.agent.email }}</span>
          </div>
        </div>
        <NuxtLink :to="`/superadmin/tenants/${data.agent.id}`" class="btn-link">
          View Agent →
        </NuxtLink>
      </div>

      <!-- Driver Info -->
      <div class="card" v-if="data.driver">
        <h2 class="card-title">👤 Driver</h2>
        <div class="info-list">
          <div class="info-row">
            <span class="label">Name</span>
            <span>{{ data.driver.first_name }} {{ data.driver.last_name }}</span>
          </div>
          <div class="info-row">
            <span class="label">Date of Birth</span>
            <span>{{ formatDOB(data.driver.date_of_birth) }}</span>
          </div>
          <div class="info-row">
            <span class="label">Email</span>
            <span>{{ data.driver.email }}</span>
          </div>
          <div class="info-row">
            <span class="label">Mobile</span>
            <span>{{ data.driver.mobile }}</span>
          </div>
          <div class="info-row">
            <span class="label">Address</span>
            <span>{{ data.driver.address_line_1 }}, {{ data.driver.city }}, {{ data.driver.postcode }}</span>
          </div>
        </div>
      </div>

      <!-- Vehicle Info -->
      <div class="card" v-if="data.vehicle">
        <h2 class="card-title">🚗 Vehicle</h2>
        <div class="info-list">
          <div class="info-row">
            <span class="label">Registration</span>
            <code class="reg">{{ data.vehicle.registration }}</code>
          </div>
          <div class="info-row">
            <span class="label">Make & Model</span>
            <span>{{ data.vehicle.make }} {{ data.vehicle.model }}</span>
          </div>
          <div class="info-row">
            <span class="label">Year</span>
            <span>{{ data.vehicle.year }}</span>
          </div>
          <div class="info-row">
            <span class="label">Value Range</span>
            <span>{{ data.vehicle.value_range }}</span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'

definePageMeta({ layout: 'superadmin' })

const auth   = useAuthStore()
const route  = useRoute()
const router = useRouter()
auth.init()

const data    = ref(null)
const loading = ref(true)
const breadcrumbs = ref([
  { label: 'Policies', to: '/superadmin/policies' },
  { label: 'Policy Detail' },
])

function formatDOB(dob) {
  if (!dob) return '—'
  const [year, month, day] = dob.split('-')
  return new Date(year, month - 1, day).toLocaleDateString('en-GB', { day: '2-digit', month: 'long', year: 'numeric' })
}

function formatDate(dt) {
  if (!dt) return '—'
  return new Date(dt).toLocaleString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

async function cancelPolicy() {
  if (!confirm('Are you sure you want to cancel this policy?')) return
  try {
    await api.delete(`/api/superadmin/policies/${route.params.id}`, auth.token)
    await load()
  } catch (e) {
    console.error(e)
  }
}

async function deletePolicy() {
  if (!confirm(`Permanently delete policy ${data.value.policy.policy_number}? This cannot be undone.`)) return
  try {
    await api.delete(`/api/superadmin/policies/${route.params.id}/permanent`, auth.token)
    router.push('/superadmin/policies')
  } catch (e) {
    console.error(e)
  }
}

async function load() {
  try {
    data.value = await api.get(`/api/superadmin/policies/${route.params.id}`, auth.token)
    breadcrumbs.value = [
      { label: 'Policies', to: '/superadmin/policies' },
      { label: `Policy #${data.value.policy.policy_number}` },
    ]
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.page-header { margin-bottom: 2rem; }
.back-link {
  color: #888; font-size: 0.85rem; text-decoration: none;
  display: inline-block; margin-bottom: 0.5rem;
}
.back-link:hover { color: var(--accent); }
.page-title { font-size: 1.6rem; font-weight: 700; color: var(--text-primary); }

.loading { text-align: center; padding: 3rem; color: #888; }
.empty-state { text-align: center; padding: 3rem; color: #888; }

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

.card-title {
  font-size: 1rem; font-weight: 700;
  color: var(--text-primary); margin-bottom: 1.25rem;
}

.info-list { display: flex; flex-direction: column; gap: 0.75rem; }

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f5f5f5;
}
.info-row:last-child { border-bottom: none; padding-bottom: 0; }

.label { color: #888; font-weight: 500; }

.policy-num {
  background: var(--brand-50); color: var(--brand-700);
  padding: 0.2rem 0.5rem; border-radius: 6px;
  font-size: 0.82rem; font-weight: 600;
}

.reg {
  font-family: monospace; background: #f5f5f5;
  padding: 0.2rem 0.5rem; border-radius: 4px;
  letter-spacing: 1px; font-size: 0.9rem;
}

.price { font-weight: 700; color: var(--text-primary); font-size: 1rem; }

.badge {
  padding: 0.25rem 0.65rem; border-radius: 50px;
  font-size: 0.72rem; font-weight: 600; text-transform: capitalize;
}
.badge-active    { background: #e6f9f0; color: #00873a; }
.badge-expired   { background: #f5f5f5; color: #888; }
.badge-cancelled { background: #fff0f0; color: #cc0000; }
.badge-pending   { background: #fff8e6; color: #b36b00; }

.btn-edit {
  display: block; width: 100%; margin-top: 1.25rem;
  padding: 0.75rem; background: var(--brand-50);
  color: var(--brand-700); border: 1px solid var(--brand-200);
  border-radius: 8px; font-size: 0.88rem;
  font-weight: 600; cursor: pointer; transition: all 0.2s;
  text-align: center; text-decoration: none;
}
.btn-edit:hover { background: var(--brand-100); }

.btn-cancel {
  width: 100%; margin-top: 0.75rem;
  padding: 0.75rem; background: #fff0f0;
  color: #cc0000; border: 1px solid #ffcccc;
  border-radius: 8px; font-size: 0.88rem;
  font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.btn-cancel:hover { background: #ffdddd; }

.btn-delete {
  width: 100%; margin-top: 0.75rem;
  padding: 0.75rem; background: #cc0000;
  color: white; border: 1px solid #cc0000;
  border-radius: 8px; font-size: 0.88rem;
  font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.btn-delete:hover { background: #a80000; }

.btn-link {
  display: inline-block; margin-top: 1rem;
  color: var(--accent); font-size: 0.85rem;
  font-weight: 600; text-decoration: none;
}
.btn-link:hover { text-decoration: underline; }

@media (max-width: 768px) {
  .detail-grid { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; gap: 0.75rem; align-items: flex-start; }
  .page-title { font-size: 1.3rem; }
  .btn-cancel { width: 100%; }
}

@media (max-width: 480px) {
  .card { padding: 1rem; }
  .info-row { flex-direction: column; gap: 0.2rem; }
  .label { min-width: unset; font-size: 0.72rem; }
}
</style>