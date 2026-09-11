<template>
  <div>
    <div class="g-header">
      <div>
        <NuxtLink to="/superadmin/tenants" class="g-back">← Back to Agents</NuxtLink>
        <h1 class="g-title">Edit Agent</h1>
      </div>
    </div>

    <div v-if="toast.show" class="g-toast" :class="toast.type">{{ toast.message }}</div>
    <div v-if="loading" class="g-loading">Loading...</div>

    <div v-else class="form-wrap">

      <div class="g-section">
        <div class="g-section-title">Agent Information</div>
        <div class="g-form-grid">
          <div class="g-field"><label>Full Name *</label><input v-model="form.name" type="text" class="g-input" /></div>
          <div class="g-field"><label>Company</label><input v-model="form.company" type="text" class="g-input" /></div>
          <div class="g-field"><label>Email *</label><input v-model="form.email" type="email" class="g-input" /></div>
          <div class="g-field"><label>Phone</label><input v-model="form.phone" type="tel" class="g-input" /></div>
        </div>
      </div>

      <div class="g-section">
        <div class="g-section-title">Access & Status</div>
        <div class="g-form-grid">
          <div class="g-field">
            <label>Status</label>
            <select v-model="form.status" class="g-input">
              <option value="active">Active</option>
              <option value="suspended">Suspended</option>
              <option value="pending">Pending</option>
            </select>
          </div>
          <div class="g-field">
            <label>Plan</label>
            <select v-model="form.plan" class="g-input">
              <option value="basic">Basic</option>
              <option value="pro">Pro</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </div>
          <div class="g-field"><label>Monthly Fee (£)</label><input v-model="form.monthly_fee" type="number" step="0.01" class="g-input" /></div>
          <div class="g-field"><label>Expires At</label><input v-model="form.expires_at" type="datetime-local" class="g-input" /></div>
        </div>

        <div class="quick-btns">
          <button class="quick-btn" @click="setExpiry(7)">+7 Days</button>
          <button class="quick-btn" @click="setExpiry(14)">+14 Days</button>
          <button class="quick-btn" @click="setExpiry(30)">+30 Days</button>
          <button class="quick-btn" @click="setExpiry(90)">+90 Days</button>
          <button class="quick-btn quick-btn-clear" @click="form.expires_at = ''">Clear</button>
        </div>
      </div>

      <div class="g-section">
        <div class="g-section-title">Change Password</div>
        <div class="g-form-grid">
          <div class="g-field"><label>New Password (leave blank to keep current)</label><input v-model="form.password" type="password" placeholder="Min 8 characters" class="g-input" /></div>
        </div>
      </div>

      <div class="form-actions">
        <NuxtLink to="/superadmin/tenants" class="g-btn g-btn-ghost">Cancel</NuxtLink>
        <button class="g-btn g-btn-primary" @click="save" :disabled="saving">
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'

definePageMeta({ layout: 'superadmin' })
const auth = useAuthStore()
auth.init()
const route = useRoute()

const loading = ref(true)
const saving  = ref(false)
const toast   = ref({ show: false, message: '', type: 'success' })

const form = ref({
  name: '', company: '', email: '', phone: '',
  status: 'active', plan: 'basic',
  monthly_fee: 0, expires_at: '', password: ''
})

function showToast(msg, type = 'success') {
  toast.value = { show: true, message: msg, type }
  setTimeout(() => toast.value.show = false, 3000)
}

function toLocalInput(d) {
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`
}

function setExpiry(days) {
  const d = new Date()
  d.setDate(d.getDate() + days)
  form.value.expires_at = toLocalInput(d)
}

onMounted(async () => {
  try {
    const data = await api.get(`/api/superadmin/tenants/${route.params.id}`, auth.token)
    form.value = {
      name:        data.name || '',
      company:     data.company || '',
      email:       data.email || '',
      phone:       data.phone || '',
      status:      data.status || 'active',
      plan:        data.plan || 'basic',
      monthly_fee: data.monthly_fee || 0,
      expires_at:  data.expires_at ? toLocalInput(new Date(data.expires_at)) : '',
      password:    '',
    }
  } catch(e) { console.error(e) }
  finally { loading.value = false }
})

async function save() {
  saving.value = true
  try {
    const payload = { ...form.value }
    if (!payload.password) delete payload.password
    if (!payload.expires_at) payload.expires_at = null
    else payload.expires_at = new Date(payload.expires_at).toISOString()

    await api.patch(`/api/superadmin/tenants/${route.params.id}`, payload, auth.token)
    showToast('Agent updated successfully!')
    setTimeout(() => navigateTo('/superadmin/tenants'), 1500)
  } catch(e) {
    showToast(e.message, 'error')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.form-wrap { max-width: 780px; display: flex; flex-direction: column; gap: 1.25rem; }

.g-input {
  padding: 0.72rem 0.875rem;
  border: 1.5px solid var(--gray-200);
  border-radius: 10px; font-size: 0.875rem; outline: none;
  transition: all 0.18s; background: white;
  color: var(--text-primary); font-family: var(--font); width: 100%;
}
.g-input:focus { border-color: var(--brand-500); box-shadow: 0 0 0 3px rgba(255,81,0,0.1); }

.g-field label { font-size: 0.8rem; font-weight: 600; color: var(--brand-800); display: block; margin-bottom: 0.4rem; }

.quick-btns { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 1rem; }
.quick-btn {
  padding: 0.4rem 0.875rem;
  background: var(--brand-100); color: var(--brand-700);
  border: 1px solid var(--brand-200); border-radius: 8px;
  font-size: 0.78rem; font-weight: 600; cursor: pointer;
  transition: all 0.18s; font-family: var(--font);
}
.quick-btn:hover { background: var(--brand-200); }
.quick-btn-clear { background: var(--gray-100); color: var(--text-muted); border-color: var(--gray-200); }

.form-actions { display: flex; gap: 1rem; justify-content: flex-end; }

@media (max-width: 768px) {
  .g-form-grid { grid-template-columns: 1fr !important; }
  .form-actions { flex-direction: column-reverse; }
  .form-actions .g-btn { width: 100%; justify-content: center; text-align: center; }
}
</style>
