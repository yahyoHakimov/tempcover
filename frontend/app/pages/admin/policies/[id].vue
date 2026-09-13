<template>
  <div>
    <AppBreadcrumb :items="breadcrumbs" />

    <div v-if="toast.show" class="g-toast" :class="toast.type">{{ toast.message }}</div>
    <div v-if="loading" class="g-loading">Loading policy…</div>

    <div v-else-if="!data" class="g-empty">
      <div class="g-empty-icon">🔍</div>
      <p class="g-empty-text">Policy not found</p>
    </div>

    <div v-else>
      <div class="page-head">
        <div class="head-left">
          <h1 class="g-title">Policy {{ data.policy.policy_number }}</h1>
          <div class="head-meta">
            <span class="g-badge" :class="'g-badge-' + data.policy.status">{{ data.policy.status }}</span>
            <span class="meta-dot">·</span>
            <span class="meta-text">Issued {{ fmtDateTime(data.policy.issued_at) }}</span>
            <template v-if="data.policy.status === 'active' && timeLeft(data.policy.end_datetime)">
              <span class="meta-dot">·</span>
              <span class="meta-left">{{ timeLeft(data.policy.end_datetime) }}</span>
            </template>
            <template v-else-if="data.policy.status === 'pending' && timeUntil(data.policy.start_datetime)">
              <span class="meta-dot">·</span>
              <span class="meta-pending">{{ timeUntil(data.policy.start_datetime) }}</span>
            </template>
            <template v-if="data.policy.version > 1">
              <span class="meta-dot">·</span>
              <span class="meta-version">Version {{ data.policy.version }} · mid-term adjustment</span>
            </template>
          </div>
        </div>
        <div class="head-actions">
          <NuxtLink v-if="isLive" :to="`/admin/policies/edit/${route.params.id}`" class="g-btn g-btn-ghost">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            Edit
          </NuxtLink>
          <button v-if="isLive" class="g-btn g-btn-danger" @click="cancelOpen = true" :disabled="busy">Cancel policy</button>
        </div>
      </div>

      <div class="detail-grid">

        <!-- Cover -->
        <div class="g-card">
          <div class="g-section-title">Cover</div>
          <div class="g-info-row"><span class="g-info-label">Cover type</span><span class="g-info-value">{{ data.policy.cover_label || coverLabel(data.policy.cover_type) }}</span></div>
          <div class="g-info-row"><span class="g-info-label">Starts</span><span class="g-info-value">{{ fmtDateTimeLong(data.policy.start_datetime) }}</span></div>
          <div class="g-info-row"><span class="g-info-label">Ends</span><span class="g-info-value">{{ fmtDateTimeLong(data.policy.end_datetime) }}</span></div>
          <div class="g-info-row"><span class="g-info-label">Price</span><span class="g-info-value price">{{ fmtMoney(data.policy.price) }}</span></div>
          <div class="g-info-row"><span class="g-info-label">Email</span>
            <span class="g-info-value">
              <span class="g-badge" :class="data.policy.email_sent ? 'g-badge-active' : 'g-badge-pending'">{{ data.policy.email_sent ? 'Sent' : 'Pending' }}</span>
              <span v-if="data.policy.email_sent_at" class="muted"> · {{ fmtDateTime(data.policy.email_sent_at) }}</span>
            </span>
          </div>
          <div v-if="data.policy.status === 'cancelled'" class="g-info-row"><span class="g-info-label">Cancelled</span>
            <span class="g-info-value">{{ fmtDateTime(data.policy.cancelled_at) }}<span v-if="data.policy.cancellation_reason" class="muted"> · {{ data.policy.cancellation_reason }}</span></span>
          </div>
        </div>

        <!-- Documents -->
        <div class="g-card">
          <div class="g-section-title">Documents</div>
          <p v-if="data.policy.status === 'cancelled'" class="docs-note">This policy is cancelled — its documents are no longer valid and cannot be sent.</p>
          <template v-else>
          <p class="docs-note">Generated from the current policy details<span v-if="data.policy.version > 1"> (version {{ data.policy.version }})</span>. The driver opens them from the emailed link.</p>
          <button class="doc-btn" @click="openPdf('certificate')" :disabled="busy">
            <span class="doc-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg></span>
            <span class="doc-name">Certificate of Motor Insurance</span>
            <span class="doc-action">Open</span>
          </button>
          <button class="doc-btn" @click="openPdf('schedule')" :disabled="busy">
            <span class="doc-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg></span>
            <span class="doc-name">Policy Schedule</span>
            <span class="doc-action">Open</span>
          </button>
          <button class="doc-btn" @click="openPdf('combined', true)" :disabled="busy">
            <span class="doc-icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></span>
            <span class="doc-name">Certificate + Schedule (PDF)</span>
            <span class="doc-action">Download</span>
          </button>
          <button class="g-btn g-btn-secondary resend" @click="resendEmail" :disabled="busy">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            {{ busy === 'email' ? 'Sending…' : (data.policy.version > 1 ? 'Resend updated documents' : 'Resend confirmation email') }}
          </button>
          </template>
        </div>

        <!-- Policy holder -->
        <div class="g-card" v-if="data.driver">
          <div class="g-section-title">Policy Holder</div>
          <div class="g-info-row"><span class="g-info-label">Name</span><span class="g-info-value">{{ data.driver.first_name }} {{ data.driver.last_name }}</span></div>
          <div class="g-info-row"><span class="g-info-label">Date of birth</span><span class="g-info-value">{{ fmtDOB(data.driver.date_of_birth) }}</span></div>
          <div class="g-info-row"><span class="g-info-label">Licence</span><span class="g-info-value mono">{{ data.driver.driving_licence }}</span></div>
          <div class="g-info-row"><span class="g-info-label">Email</span><span class="g-info-value"><a :href="`mailto:${data.driver.email}`" class="link">{{ data.driver.email }}</a></span></div>
          <div class="g-info-row"><span class="g-info-label">Mobile</span><span class="g-info-value">{{ data.driver.mobile }}</span></div>
          <div class="g-info-row"><span class="g-info-label">Address</span><span class="g-info-value">{{ address }}</span></div>
          <div class="g-info-row"><span class="g-info-label">Occupation</span><span class="g-info-value">{{ data.driver.occupation }}</span></div>
        </div>

        <!-- Vehicle -->
        <div class="g-card" v-if="data.vehicle">
          <div class="g-section-title">Vehicle</div>
          <div class="g-info-row"><span class="g-info-label">Registration</span><span class="g-info-value"><span class="reg">{{ data.vehicle.registration }}</span></span></div>
          <div class="g-info-row"><span class="g-info-label">Make & model</span><span class="g-info-value">{{ data.vehicle.make }} {{ data.vehicle.model }}</span></div>
          <div class="g-info-row"><span class="g-info-label">Year</span><span class="g-info-value">{{ data.vehicle.year }}</span></div>
          <div class="g-info-row" v-if="data.vehicle.color"><span class="g-info-label">Colour</span><span class="g-info-value">{{ data.vehicle.color }}</span></div>
          <div class="g-info-row"><span class="g-info-label">Value</span><span class="g-info-value">{{ data.vehicle.value_range }}</span></div>
        </div>

      </div>
    </div>

    <!-- Cancel modal -->
    <div v-if="cancelOpen" class="modal-backdrop" @click.self="cancelOpen = false">
      <div class="modal" role="dialog" aria-modal="true" aria-labelledby="cancel-title">
        <h2 id="cancel-title" class="modal-title">Cancel policy {{ data?.policy.policy_number }}</h2>
        <p class="modal-text">Cover ends immediately and the driver is emailed a cancellation notice. This cannot be undone.</p>
        <div class="g-field" style="margin-bottom:0.9rem;">
          <label>Reason</label>
          <select v-model="cancelReason">
            <option v-for="r in CANCEL_REASONS" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
        <div class="g-field" v-if="cancelReason === 'Other'">
          <label>Details</label>
          <input v-model.trim="cancelNote" type="text" maxlength="200" placeholder="Short note for the record" />
        </div>
        <div class="modal-actions">
          <button class="g-btn g-btn-ghost" @click="cancelOpen = false" :disabled="busy">Keep policy</button>
          <button class="g-btn g-btn-danger" @click="confirmCancel" :disabled="busy">{{ busy === 'cancel' ? 'Cancelling…' : 'Cancel policy' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'
import { fmtDateTime, fmtDateTimeLong, fmtDOB, fmtMoney, timeLeft, timeUntil } from '~/utils/format'

definePageMeta({ layout: 'admin' })

const auth = useAuthStore()
auth.init()
const route = useRoute()

const data = ref(null)
const loading = ref(true)
const busy = ref(false)
const toast = ref({ show: false, message: '', type: 'success' })
const breadcrumbs = ref([{ label: 'Policies', to: '/admin/policies' }, { label: 'Policy' }])

const CANCEL_REASONS = ['Customer request', 'Issued in error', 'Payment not received', 'Vehicle no longer required', 'Other']
const cancelOpen = ref(false)
const cancelReason = ref(CANCEL_REASONS[0])
const cancelNote = ref('')
const isLive = computed(() => ['active', 'pending'].includes(data.value?.policy?.status))

useHead({ title: computed(() => data.value ? `Policy ${data.value.policy.policy_number}` : 'Policy') })

function showToast(msg, type = 'success') {
  toast.value = { show: true, message: msg, type }
  setTimeout(() => (toast.value.show = false), 3500)
}

const COVER = {
  fully_comprehensive:    'Fully Comprehensive',
  third_party_fire_theft: 'Third Party, Fire & Theft',
  third_party_only:       'Third Party Only',
}
const coverLabel = (c) => COVER[c] || c

const address = computed(() => {
  const d = data.value?.driver
  if (!d) return ''
  return [d.address_line_1, d.address_line_2, d.city, d.postcode].filter(Boolean).join(', ')
})

async function load() {
  loading.value = true
  try {
    data.value = await api.get(`/api/policies/${route.params.id}`, auth.token)
    breadcrumbs.value = [{ label: 'Policies', to: '/admin/policies' }, { label: `Policy ${data.value.policy.policy_number}` }]
  } catch (e) {
    data.value = null
    showToast(e.message, 'error')
  } finally { loading.value = false }
}

async function confirmCancel() {
  busy.value = 'cancel'
  try {
    const reason = cancelReason.value === 'Other' ? (cancelNote.value || 'Other') : cancelReason.value
    const updated = await api.post(`/api/policies/${route.params.id}/cancel`, { reason }, auth.token)
    data.value.policy.status = updated.status
    data.value.policy.cancelled_at = updated.cancelled_at
    data.value.policy.cancellation_reason = updated.cancellation_reason
    cancelOpen.value = false
    showToast('Policy cancelled — the driver has been notified')
  } catch (e) { showToast(e.message, 'error') }
  finally { busy.value = false }
}

async function resendEmail() {
  busy.value = 'email'
  try {
    await api.post(`/api/policies/${route.params.id}/resend-email`, {}, auth.token)
    showToast('Confirmation email queued')
    setTimeout(load, 2500)
  } catch (e) { showToast(e.message, 'error') }
  finally { busy.value = false }
}

// Admin PDF routes require the JWT, so fetch the file and hand the browser a blob URL.
async function openPdf(kind, download = false) {
  const win = download ? null : window.open('', '_blank')   // open synchronously so popup blockers allow it
  busy.value = kind
  try {
    const res = await fetch(api.url(`/api/v1/pdf/admin/${kind}/${route.params.id}`), {
      headers: { Authorization: `Bearer ${auth.token}` },
    })
    if (!res.ok) throw new Error('Could not generate the document')
    const url = URL.createObjectURL(await res.blob())
    if (download) {
      const a = document.createElement('a')
      a.href = url
      a.download = `policy_${data.value.policy.policy_number}.pdf`
      document.body.appendChild(a); a.click(); a.remove()
    } else if (win) {
      win.location.href = url
    } else {
      window.open(url, '_blank')
    }
    setTimeout(() => URL.revokeObjectURL(url), 60_000)
  } catch (e) {
    win?.close()
    showToast(e.message, 'error')
  } finally { busy.value = false }
}

onMounted(load)
</script>

<style scoped>
.page-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
.head-meta { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem; flex-wrap: wrap; font-size: 0.85rem; }
.meta-dot { color: var(--gray-300); }
.meta-text { color: var(--text-muted); }
.meta-left { color: var(--brand-600); font-weight: 500; }
.meta-pending { color: var(--warning); font-weight: 500; }
.meta-version { color: var(--text-secondary); }
.muted { color: var(--text-muted); font-weight: 400; }

.modal-backdrop { position: fixed; inset: 0; background: rgba(17,24,39,0.45); display: flex; align-items: center; justify-content: center; padding: 1rem; z-index: 100; }
.modal { background: white; border-radius: 14px; padding: 1.5rem; width: 100%; max-width: 440px; box-shadow: 0 20px 60px rgba(0,0,0,0.25); }
.modal-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem; }
.modal-text { font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 1.1rem; }
.modal-actions { display: flex; gap: 0.6rem; justify-content: flex-end; margin-top: 1.25rem; }
.head-actions { display: flex; gap: 0.6rem; flex-wrap: wrap; }

.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }
.price { font-weight: 700; font-size: 1.05rem; color: var(--brand-600); }
.mono { font-family: 'Courier New', monospace; letter-spacing: 0.5px; }
.reg { font-family: 'Courier New', monospace; font-weight: 700; background: #FFE600; color: #111; padding: 0.15rem 0.55rem; border-radius: 4px; letter-spacing: 1px; border: 1px solid #E5CF00; }
.link { color: var(--brand-600); text-decoration: none; }
.link:hover { text-decoration: underline; }

.docs-note { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.9rem; }
.doc-btn {
  display: flex; align-items: center; gap: 0.75rem; width: 100%; text-align: left;
  padding: 0.8rem 0.9rem; margin-bottom: 0.5rem; background: white; border: 1.5px solid var(--gray-200); border-radius: 10px;
  cursor: pointer; transition: all 0.15s; color: var(--text-primary); font-family: var(--font);
}
.doc-btn:hover:not(:disabled) { border-color: var(--brand-400); background: var(--brand-50); }
.doc-btn:disabled { opacity: 0.6; cursor: wait; }
.doc-icon { color: var(--brand-500); display: flex; }
.doc-name { flex: 1; font-size: 0.875rem; font-weight: 500; }
.doc-action { font-size: 0.78rem; font-weight: 600; color: var(--brand-600); }
.resend { width: 100%; margin-top: 0.5rem; }

@media (max-width: 768px) {
  .detail-grid { grid-template-columns: 1fr; }
  .head-actions { width: 100%; }
  .head-actions .g-btn { flex: 1; }
}
</style>
