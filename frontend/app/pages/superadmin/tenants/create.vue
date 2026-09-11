<template>
  <div>
    <div class="page-header">
      <div>
        <NuxtLink to="/superadmin/tenants" class="back-link">← Back to Agents</NuxtLink>
        <h1 class="page-title">Add New Agent</h1>
      </div>
    </div>

    <div class="form-wrap">
      <!-- Error -->
      <div v-if="error" class="error-box">{{ error }}</div>

      <!-- Success -->
      <div v-if="success" class="toast-success">
        <span>✅</span>
        <span>Agent created successfully! Redirecting...</span>
      </div>

      <form @submit.prevent="handleSubmit" v-if="!success">

        <!-- Personal Info -->
        <div class="form-section">
          <h2 class="section-title">👤 Agent Information</h2>
          <div class="form-grid">
            <div class="field">
              <label>Full Name *</label>
              <input v-model="form.name" type="text" placeholder="John Smith" required />
            </div>
            <div class="field">
              <label>Company Name</label>
              <input v-model="form.company" type="text" placeholder="Smith Insurance Ltd" />
            </div>
            <div class="field">
              <label>Email *</label>
              <input v-model="form.email" type="email" placeholder="john@example.com" required />
            </div>
            <div class="field">
              <label>Phone</label>
              <input v-model="form.phone" type="tel" placeholder="+44 7700 900000" />
            </div>
          </div>
        </div>

        <!-- Login Credentials -->
        <div class="form-section">
          <h2 class="section-title">🔐 Login Credentials</h2>
          <div class="form-grid">
            <div class="field">
              <label>Username *</label>
              <input v-model="form.username" type="text" placeholder="johnsmith" required />
            </div>
            <div class="field">
              <label>Password *</label>
              <div class="password-wrap">
                <input
                  v-model="form.password"
                  :type="showPwd ? 'text' : 'password'"
                  placeholder="Min 8 characters"
                  required
                />
                <button type="button" class="eye-btn" @click="showPwd = !showPwd">
                  {{ showPwd ? '🙈' : '👁️' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Session Expiry -->
        <div class="form-section">
          <h2 class="section-title">⏰ Session Expiry</h2>
          <p class="section-desc">Set when this agent's access will expire. Leave blank for no expiry.</p>

          <div class="form-grid">
            <div class="field">
              <label>Expiry Date & Time</label>
              <input v-model="form.expires_at" type="datetime-local" />
            </div>

            <!-- Quick select buttons -->
            <div class="field">
              <label>Quick Select</label>
              <div class="quick-btns">
                <button type="button" class="quick-btn" @click="setExpiry(7)">7 Days</button>
                <button type="button" class="quick-btn" @click="setExpiry(14)">14 Days</button>
                <button type="button" class="quick-btn" @click="setExpiry(30)">30 Days</button>
                <button type="button" class="quick-btn" @click="setExpiry(90)">90 Days</button>
                <button type="button" class="quick-btn quick-btn-clear" @click="form.expires_at = ''">Clear</button>
              </div>
            </div>
          </div>

          <!-- Preview countdown -->
          <div v-if="form.expires_at" class="expiry-preview">
            <span class="expiry-label">Agent will have access until:</span>
            <span class="expiry-value">{{ formatDate(form.expires_at) }}</span>
            <span class="expiry-days">({{ daysUntil(form.expires_at) }} days from now)</span>
          </div>
        </div>

        <!-- Submit -->
        <div class="form-actions">
          <NuxtLink to="/superadmin/tenants" class="btn-cancel">Cancel</NuxtLink>
          <button type="submit" class="btn-submit" :disabled="loading">
            <span v-if="loading">Creating...</span>
            <span v-else>Create Agent</span>
          </button>
        </div>

      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'

definePageMeta({ layout: 'superadmin' })

const auth = useAuthStore()
auth.init()

const loading = ref(false)
const error = ref('')
const success = ref(false)
const showPwd = ref(false)

const form = ref({
  name: '',
  company: '',
  email: '',
  phone: '',
  username: '',
  password: '',
  expires_at: '',
})

function toLocalInput(d) {
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`
}

function setExpiry(days) {
  const d = new Date()
  d.setDate(d.getDate() + days)
  // datetime-local format: YYYY-MM-DDTHH:MM
  form.value.expires_at = toLocalInput(d)
}

function formatDate(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleDateString('en-GB', {
    day: '2-digit', month: 'long', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

function daysUntil(dt) {
  const diff = new Date(dt) - new Date()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
}

async function handleSubmit() {
  error.value = ''
  loading.value = true

  try {
    const payload = {
      ...form.value,
      monthly_fee: parseFloat(form.value.monthly_fee) || 0,
      expires_at: form.value.expires_at ? new Date(form.value.expires_at).toISOString() : null,
    }

    await api.post('/api/superadmin/tenants', payload, auth.token)
    
    // 2 soniya success ko'rsat, keyin redirect
    success.value = true
    setTimeout(() => {
      navigateTo('/superadmin/tenants')
    }, 2000)
    
  } catch (e) {
    error.value = e.message || 'Failed to create agent'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-header { margin-bottom: 2rem; }
.back-link { color: var(--text-muted); font-size: 0.85rem; text-decoration: none; display: inline-block; margin-bottom: 0.5rem; }
.back-link:hover { color: var(--accent); }
.page-title { font-size: 1.6rem; font-weight: 800; color: var(--text-primary); }

.form-wrap { max-width: 800px; }

.error-box {
  background: var(--error-bg); border: 1px solid var(--error-border);
  border-radius: 10px; padding: 0.75rem 1rem;
  color: var(--error); font-size: 0.88rem; margin-bottom: 1.5rem;
}

.form-section {
  background: white;
  border-radius: var(--card-radius);
  padding: 1.5rem;
  margin-bottom: 1.25rem;
  box-shadow: var(--card-shadow);
  border: 1px solid rgba(0,0,0,0.04);
}

.section-title {
  font-size: 0.875rem; font-weight: 700;
  color: var(--brand-800); margin-bottom: 0.25rem;
  display: flex; align-items: center; gap: 0.5rem;
}
.section-desc { color: var(--text-muted); font-size: 0.82rem; margin-bottom: 1.25rem; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }

.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field label { font-size: 0.8rem; font-weight: 600; color: var(--brand-800); }

.field input,
.field select {
  padding: 0.72rem 0.875rem;
  border: 1.5px solid var(--gray-200);
  border-radius: 10px; font-size: 0.875rem; outline: none;
  transition: all 0.18s; font-family: var(--font);
  background: white; color: var(--text-primary);
}
.field input:focus,
.field select:focus { border-color: var(--brand-500); box-shadow: 0 0 0 3px rgba(255,81,0,0.1); }

.password-wrap { position: relative; }
.password-wrap input { width: 100%; padding-right: 3rem; }
.eye-btn { position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; font-size: 1rem; }

.quick-btns { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.quick-btn {
  padding: 0.45rem 0.85rem;
  background: var(--brand-100); color: var(--brand-700);
  border: 1px solid var(--brand-200); border-radius: 8px;
  font-size: 0.78rem; font-weight: 600; cursor: pointer; transition: all 0.18s;
  font-family: var(--font);
}
.quick-btn:hover { background: var(--brand-200); }
.quick-btn-clear { background: var(--gray-100); color: var(--text-muted); border-color: var(--gray-200); }
.quick-btn-clear:hover { background: var(--gray-200); }

.expiry-preview {
  margin-top: 1rem; padding: 0.75rem 1rem;
  background: var(--success-bg); border: 1px solid var(--success-border);
  border-radius: 10px; display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;
}
.expiry-label { font-size: 0.82rem; color: var(--text-secondary); }
.expiry-value { font-weight: 700; color: var(--success); font-size: 0.875rem; }
.expiry-days { font-size: 0.78rem; color: var(--text-muted); }

.form-actions { display: flex; gap: 1rem; justify-content: flex-end; margin-top: 1.5rem; }

.toast-success {
  position: fixed; top: 2rem; right: 2rem;
  background: var(--success); color: white;
  padding: 1rem 1.5rem; border-radius: 12px;
  display: flex; align-items: center; gap: 0.75rem;
  font-weight: 600; font-size: 0.95rem;
  box-shadow: 0 8px 24px rgba(5,150,105,0.3);
  animation: slideIn 0.3s ease; z-index: 9999;
}
@keyframes slideIn { from { transform: translateX(100px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

.btn-cancel {
  padding: 0.75rem 1.5rem;
  background: var(--gray-100); color: var(--text-secondary);
  border: 1px solid var(--gray-200); border-radius: 10px;
  font-size: 0.875rem; font-weight: 600;
  text-decoration: none; display: inline-block; transition: all 0.18s;
  font-family: var(--font);
}
.btn-cancel:hover { background: var(--gray-200); }

.btn-submit {
  padding: 0.75rem 2rem;
  background: var(--brand-500);
  color: white; border: none; border-radius: 10px;
  font-size: 0.875rem; font-weight: 700;
  cursor: pointer; transition: all 0.18s;
  font-family: var(--font);
  box-shadow: 0 4px 14px rgba(255,81,0,0.3);
}
.btn-submit:hover:not(:disabled) { background: var(--brand-600); transform: translateY(-1px); }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr; }
  .page-title { font-size: 1.3rem; }
  .form-wrap { max-width: 100%; }
  .form-section { padding: 1.25rem 1rem; }
  .form-actions { flex-direction: column-reverse; gap: 0.75rem; }
  .btn-cancel, .btn-submit { width: 100%; text-align: center; }
  .toast-success { top: auto; bottom: 1rem; right: 1rem; left: 1rem; }
  .quick-btns { gap: 0.4rem; }
  .quick-btn { padding: 0.4rem 0.65rem; font-size: 0.75rem; }
}
</style>