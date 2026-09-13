<template>
  <div>
    <div class="page-head">
      <div>
        <h1 class="g-title">{{ heading.title }}</h1>
        <p class="g-subtitle">{{ heading.subtitle }}</p>
      </div>
      <NuxtLink to="/admin/policies/create" class="g-btn g-btn-primary">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Create Policy
      </NuxtLink>
    </div>

    <div class="toolbar">
      <div class="chips">
        <button v-for="c in CHIPS" :key="c.key" class="chip" :class="{ on: filter === c.key }" @click="setFilter(c.key)">
          {{ c.label }}
        </button>
      </div>
      <input v-model="query" type="search" class="g-input search" placeholder="Search policy no., driver or registration…" />
    </div>

    <div v-if="loading" class="g-loading">Loading policies…</div>

    <div v-else-if="filtered.length === 0" class="g-empty">
      <div class="g-empty-icon">📄</div>
      <p class="g-empty-text">{{ policies.length === 0 ? 'No policies in this view yet' : 'No policies match your search' }}</p>
      <NuxtLink v-if="policies.length === 0 && filter === ''" to="/admin/policies/create" class="g-btn g-btn-primary" style="margin-top:1.25rem;width:auto;">Create your first policy</NuxtLink>
    </div>

    <div v-else class="list">
      <p class="count">{{ filtered.length }} {{ filtered.length === 1 ? 'policy' : 'policies' }}</p>

      <NuxtLink v-for="p in filtered" :key="p.id" :to="`/admin/policies/${p.id}`" class="row">
        <div class="row-main">
          <span class="g-policy-num">{{ p.policy_number }}</span>
          <div class="row-who">
            <span class="row-name">{{ driverName(p) }}</span>
            <span class="row-reg">{{ vehicleLabel(p) }}</span>
          </div>
        </div>

        <div class="row-dates">
          <span class="row-date"><span class="lbl">From</span>{{ fmtDateTime(p.start_datetime) }}</span>
          <span class="row-date"><span class="lbl">To</span>{{ fmtDateTime(p.end_datetime) }}</span>
          <span v-if="p.status === 'active' && timeLeft(p.end_datetime)" class="row-left">{{ timeLeft(p.end_datetime) }}</span>
          <span v-else-if="p.status === 'pending' && timeUntil(p.start_datetime)" class="row-left pending">{{ timeUntil(p.start_datetime) }}</span>
        </div>

        <div class="row-price">{{ fmtMoney(p.price) }}</div>

        <div class="row-status">
          <span class="g-badge" :class="'g-badge-' + p.status">{{ p.status }}</span>
          <span class="mail" :class="p.email_sent ? 'sent' : 'pending'">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            {{ p.email_sent ? 'Email sent' : 'Email pending' }}
          </span>
        </div>

        <svg class="row-chevron" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'
import { fmtDateTime, fmtMoney, timeLeft, timeUntil } from '~/utils/format'

definePageMeta({ layout: 'admin' })
useHead({ title: 'Policies' })

const auth = useAuthStore()
auth.init()
const route = useRoute()
const router = useRouter()

const CHIPS = [
  { key: '',             label: 'All' },
  { key: 'active',       label: 'Active' },
  { key: 'pending',      label: 'Pending' },
  { key: 'expiring3',    label: 'Expiring in 3 days' },
  { key: 'expiringweek', label: 'Expiring this week' },
  { key: 'expired',      label: 'Expired' },
  { key: 'cancelled',    label: 'Cancelled' },
]
const STATUS_FILTERS = ['active', 'pending', 'cancelled', 'expired']
const EXPIRY_FILTERS = ['expiring3', 'expiringweek']

const policies = ref([])
const drivers  = ref({})
const vehicles = ref({})
const loading  = ref(true)
const query    = ref(String(route.query.q || ''))
const filter   = ref(initialFilter())

function initialFilter() {
  const q = String(route.query.filter ?? route.query.status ?? '')
  return [...STATUS_FILTERS, ...EXPIRY_FILTERS].includes(q) ? q : ''
}

const heading = computed(() => {
  switch (filter.value) {
    case 'expiring3':    return { title: 'Expiring within 3 days', subtitle: 'Urgent renewals needed' }
    case 'expiringweek': return { title: 'Expiring this week',     subtitle: 'Weekly renewal overview' }
    case 'active':       return { title: 'Active Policies',        subtitle: 'Policies currently in force' }
    case 'pending':      return { title: 'Pending Policies',       subtitle: 'Issued, cover has not started yet' }
    case 'expired':      return { title: 'Expired Policies',       subtitle: 'Policies past their end date' }
    case 'cancelled':    return { title: 'Cancelled Policies',     subtitle: 'Policies cancelled before their end date' }
    default:             return { title: 'Created Policies',       subtitle: 'All policies created by your account' }
  }
})

function setFilter(key) {
  filter.value = key
  const q = {}
  if (EXPIRY_FILTERS.includes(key)) q.filter = key
  else if (STATUS_FILTERS.includes(key)) q.status = key
  router.replace({ query: q })
  load()
}

async function load() {
  loading.value = true
  try {
    let url = '/api/policies/'
    if (EXPIRY_FILTERS.includes(filter.value)) url += `?filter=${filter.value}`
    let data = await api.get(url, auth.token)
    if (STATUS_FILTERS.includes(filter.value)) data = data.filter(p => p.status === filter.value)
    policies.value = data
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function loadLookups() {
  try {
    const [d, v] = await Promise.all([api.get('/api/drivers/', auth.token), api.get('/api/vehicles/', auth.token)])
    drivers.value  = Object.fromEntries(d.map(x => [x.id, x]))
    vehicles.value = Object.fromEntries(v.map(x => [x.id, x]))
  } catch (e) { console.error(e) }
}

function driverName(p) {
  const d = drivers.value[p.driver_id]
  return d ? `${d.first_name} ${d.last_name}` : '—'
}
function vehicleLabel(p) {
  const v = vehicles.value[p.vehicle_id]
  return v ? `${v.registration} · ${v.make} ${v.model}` : '—'
}

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return policies.value
  return policies.value.filter(p =>
    p.policy_number.toLowerCase().includes(q) ||
    driverName(p).toLowerCase().includes(q) ||
    vehicleLabel(p).toLowerCase().includes(q)
  )
})

onMounted(() => { load(); loadLookups() })
</script>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }

.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.25rem; }
.chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.search { max-width: 320px; padding: 0.6rem 0.9rem; font-size: 0.875rem; }

.count { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.75rem; }
.list { display: flex; flex-direction: column; }

.row {
  display: grid; grid-template-columns: 1.6fr 1.3fr auto auto 20px; align-items: center; gap: 1.25rem;
  background: var(--card-bg); border: 1px solid var(--card-border); border-radius: var(--card-radius);
  box-shadow: var(--card-shadow); padding: 1.1rem 1.25rem; margin-bottom: 0.75rem;
  text-decoration: none; color: inherit; transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
}
.row:hover { border-color: var(--brand-300); box-shadow: var(--card-shadow-hover); transform: translateY(-1px); }
.row:hover .row-chevron { color: var(--brand-500); transform: translateX(3px); }

.row-main { display: flex; align-items: center; gap: 0.9rem; min-width: 0; }
.row-who { display: flex; flex-direction: column; gap: 0.15rem; min-width: 0; }
.row-name { font-weight: 500; color: var(--text-primary); font-size: 0.95rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.row-reg { font-size: 0.8rem; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.row-dates { display: flex; flex-direction: column; gap: 0.2rem; font-size: 0.82rem; color: var(--text-secondary); }
.row-date .lbl { display: inline-block; width: 38px; color: var(--text-muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.4px; }
.row-left { font-size: 0.74rem; color: var(--brand-600); font-weight: 500; margin-top: 0.1rem; }
.row-left.pending { color: var(--warning); }

.row-price { font-weight: 700; color: var(--text-primary); font-size: 1rem; white-space: nowrap; }

.row-status { display: flex; flex-direction: column; align-items: flex-end; gap: 0.35rem; }
.mail { display: inline-flex; align-items: center; gap: 0.3rem; font-size: 0.72rem; font-weight: 500; }
.mail.sent { color: var(--success); }
.mail.pending { color: var(--warning); }

.row-chevron { color: var(--gray-400); transition: color 0.2s, transform 0.2s; }

@media (max-width: 900px) {
  .row { grid-template-columns: 1fr auto 20px; grid-template-areas: "main status chev" "dates price chev"; row-gap: 0.75rem; }
  .row-main { grid-area: main; }
  .row-status { grid-area: status; }
  .row-dates { grid-area: dates; }
  .row-price { grid-area: price; text-align: right; }
  .row-chevron { grid-area: chev; }
}
@media (max-width: 640px) {
  .page-head .g-btn { width: 100%; }
  .search { max-width: 100%; width: 100%; }
  .row { padding: 1rem; }
  .row-main { flex-direction: column; align-items: flex-start; gap: 0.4rem; }
}
</style>
