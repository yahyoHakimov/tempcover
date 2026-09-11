<template>
  <div>
    <AppBreadcrumb :items="[
      { label: 'Policies', to: '/superadmin/policies' },
      { label: 'Create New Policy' },
    ]" />

    <div class="page-header">
      <div>
        <h1 class="page-title">Create New Policy</h1>
      </div>
    </div>

    <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.message }}</div>

    <div class="form-wrap">

      <!-- Driver -->
      <div class="section-card">
        <h2 class="section-title">1. Driver Details</h2>
        <div class="field" style="margin-bottom:1rem">
          <label>Load Saved Driver</label>
          <AppSearchSelect
            v-model="selectedDriverObj"
            :options="drivers"
            :get-label="d => `${d.first_name} ${d.last_name}`"
            placeholder="Search or select a driver..."
            removable
            @select="loadDriver"
            @remove="deleteDriver"
          />
        </div>
        <div class="form-grid">
          <div class="field"><label>First Name *</label><input v-model="driver.first_name" type="text" placeholder="John" /></div>
          <div class="field"><label>Last Name *</label><input v-model="driver.last_name" type="text" placeholder="Smith" /></div>
          <div class="field"><label>Date of Birth *</label><input v-model="driver.date_of_birth" type="date" /></div>
          <div class="field"><label>Driving Licence *</label><input v-model="driver.driving_licence" type="text" /></div>
          <div class="field"><label>Mobile *</label><input v-model="driver.mobile" type="tel" /></div>
          <div class="field"><label>Email *</label><input v-model="driver.email" type="email" /></div>
          <div class="field"><label>Address Line 1 *</label><input v-model="driver.address_line_1" type="text" /></div>
          <div class="field"><label>City *</label><input v-model="driver.city" type="text" /></div>
          <div class="field"><label>Postcode *</label><input v-model="driver.postcode" type="text" /></div>
          <div class="field"><label>Occupation *</label><input v-model="driver.occupation" type="text" /></div>
        </div>
        <button class="btn-save" @click="saveDriver" :disabled="savingDriver">{{ savingDriver ? 'Saving...' : 'Save Driver' }}</button>
        <div v-if="selectedDriverId" class="saved-badge">✅ Driver saved</div>
      </div>

      <!-- Vehicle -->
      <div class="section-card">
        <h2 class="section-title">2. Vehicle Details</h2>
        <div class="field" style="margin-bottom:1rem">
          <label>Load Saved Vehicle</label>
          <AppSearchSelect
            v-model="selectedVehicleObj"
            :options="vehicles"
            :get-label="v => `${v.registration} — ${v.make} ${v.model}`"
            placeholder="Search or select a vehicle..."
            @select="loadVehicle"
          />
        </div>
        <div class="form-grid">
          <div class="field"><label>Registration *</label><input v-model="vehicle.registration" type="text" placeholder="TY24 HHD" /></div>
          <div class="field"><label>Make *</label><input v-model="vehicle.make" type="text" placeholder="LAND ROVER" /></div>
          <div class="field"><label>Model *</label><input v-model="vehicle.model" type="text" placeholder="RANGE ROVER SPORT" /></div>
          <div class="field"><label>Year *</label><input v-model="vehicle.year" type="number" placeholder="2024" /></div>
          <div class="field"><label>Vehicle Value *</label>
            <select v-model="vehicle.value_range">
              <option value="">Select value</option>
              <option value="£0-10000">£0 - £10,000</option>
              <option value="£10001-25000">£10,001 - £25,000</option>
              <option value="£25001-50000">£25,001 - £50,000</option>
              <option value="£50001-75000">£50,001 - £75,000</option>
              <option value="£75001-100000">£75,001 - £100,000</option>
              <option value="£100000+">£100,000+</option>
            </select>
          </div>
        </div>
        <button class="btn-save" @click="saveVehicle" :disabled="savingVehicle">{{ savingVehicle ? 'Saving...' : 'Save Vehicle' }}</button>
        <div v-if="selectedVehicleId" class="saved-badge">✅ Vehicle saved</div>
      </div>

      <!-- Policy -->
      <div class="section-card">
        <h2 class="section-title">3. Policy Details</h2>
        <div class="form-grid">
          <div class="field"><label>Start Date *</label><input v-model="policy.start_date" type="date" /></div>
          <div class="field"><label>Start Time *</label><input v-model="policy.start_time" type="time" /></div>
          <div class="field"><label>End Date *</label><input v-model="policy.end_date" type="date" /></div>
          <div class="field"><label>End Time *</label><input v-model="policy.end_time" type="time" /></div>
          <div class="field full-width"><label>Policy Price (£) *</label><input v-model="policy.price" type="number" step="0.01" min="0" placeholder="0.00" /></div>
        </div>
      </div>

      <button class="btn-create" @click="createPolicy" :disabled="creating">
        <span v-if="creating">Creating...</span>
        <span v-else>+ Create Policy</span>
      </button>
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

// The internal "house" agent the super admin issues policies as (resolved from /api/auth/me)
const houseTenantId = ref(null)

const drivers  = ref([])
const vehicles = ref([])
const savingDriver  = ref(false)
const savingVehicle = ref(false)
const creating = ref(false)
const selectedDriverId  = ref(null)
const selectedVehicleId = ref(null)
const selectedDriverObj  = ref(null)
const selectedVehicleObj = ref(null)
const toast = ref({ show: false, message: '', type: 'success' })

const driver = ref({ first_name:'', last_name:'', date_of_birth:'', driving_licence:'', mobile:'', email:'', address_line_1:'', city:'', postcode:'', occupation:'' })
const vehicle = ref({ registration:'', make:'', model:'', year:'', value_range:'' })
const policy = ref({ start_date:'', start_time:'', end_date:'', end_time:'', price:'' })

function showToast(msg, type='success') {
  toast.value = { show:true, message:msg, type }
  setTimeout(() => toast.value.show = false, 3000)
}

function loadDriver(d) {
  if (!d) return
  driver.value = { ...d }
  selectedDriverId.value = d.id
  showToast('Driver loaded!')
}

function loadVehicle(v) {
  if (!v) return
  vehicle.value = { ...v }
  selectedVehicleId.value = v.id
  showToast('Vehicle loaded!')
}

async function saveDriver() {
  if (!driver.value.first_name || !driver.value.last_name || !driver.value.email) { showToast('Fill required fields', 'error'); return }
  savingDriver.value = true
  try {
    const saved = await api.post(`/api/superadmin/tenants/${houseTenantId.value}/drivers`, driver.value, auth.token)
    selectedDriverId.value = saved.id
    drivers.value.push(saved)
    showToast('Driver saved!')
  } catch(e) { showToast(e.message, 'error') }
  finally { savingDriver.value = false }
}

async function deleteDriver(d) {
  if (!confirm(`Delete driver ${d.first_name} ${d.last_name}? Their old (cancelled/expired) policy records will also be removed. This cannot be undone.`)) return
  try {
    await api.delete(`/api/superadmin/drivers/${d.id}`, auth.token)
    drivers.value = drivers.value.filter(x => x.id !== d.id)
    if (selectedDriverId.value === d.id) {
      selectedDriverId.value = null
      selectedDriverObj.value = null
    }
    showToast('Driver deleted!')
  } catch(e) { showToast(e.message, 'error') }
}

async function saveVehicle() {
  if (!vehicle.value.registration || !vehicle.value.make || !vehicle.value.value_range) { showToast('Fill required fields', 'error'); return }
  savingVehicle.value = true
  try {
    const saved = await api.post(`/api/superadmin/tenants/${houseTenantId.value}/vehicles`, { ...vehicle.value, year: parseInt(vehicle.value.year) }, auth.token)
    selectedVehicleId.value = saved.id
    vehicles.value.push(saved)
    showToast('Vehicle saved!')
  } catch(e) { showToast(e.message, 'error') }
  finally { savingVehicle.value = false }
}

async function createPolicy() {
  if (!selectedDriverId.value) { showToast('Save or select a driver', 'error'); return }
  if (!selectedVehicleId.value) { showToast('Save or select a vehicle', 'error'); return }
  if (!policy.value.start_date || !policy.value.end_date || !policy.value.price) { showToast('Fill all policy details', 'error'); return }
  creating.value = true
  try {
    const created = await api.post('/api/superadmin/policies', {
      tenant_id: houseTenantId.value,
      driver_id: selectedDriverId.value,
      vehicle_id: selectedVehicleId.value,
      start_datetime: `${policy.value.start_date}T${policy.value.start_time || '00:00'}`,
      end_datetime: `${policy.value.end_date}T${policy.value.end_time || '00:00'}`,
      price: parseFloat(policy.value.price),
      cover_type: 'fully_comprehensive',
    }, auth.token)
    showToast(`Policy ${created.policy_number} created!`)
    setTimeout(() => navigateTo('/superadmin/policies'), 2000)
  } catch(e) { showToast(e.message, 'error') }
  finally { creating.value = false }
}

onMounted(async () => {
  try {
    const me = await api.get('/api/auth/me', auth.token)
    if (!me.user || me.user.username === auth.username) {
      showToast('House agent is not configured — run backend/seed.py first', 'error')
      return
    }
    houseTenantId.value = me.user.id
    const [d, v] = await Promise.all([
      api.get(`/api/superadmin/tenants/${houseTenantId.value}/drivers`, auth.token),
      api.get(`/api/superadmin/tenants/${houseTenantId.value}/vehicles`, auth.token),
    ])
    drivers.value  = d
    vehicles.value = v
  } catch(e) { console.error(e) }
})
</script>

<style scoped>
.page-header { margin-bottom: 2rem; }
.back-link { color: var(--text-muted); font-size: 0.85rem; text-decoration: none; display: inline-block; margin-bottom: 0.5rem; }
.back-link:hover { color: var(--accent); }
.page-title { font-size: 1.6rem; font-weight: 800; color: var(--text-primary); }
.form-wrap { max-width: 800px; display: flex; flex-direction: column; gap: 1.25rem; }
.toast { position: fixed; top: 1.5rem; right: 1.5rem; padding: 0.85rem 1.25rem; border-radius: 12px; font-weight: 600; font-size: 0.875rem; z-index: 9999; box-shadow: 0 8px 24px rgba(0,0,0,0.15); }
.toast.success { background: #059669; color: white; }
.toast.error   { background: #dc2626; color: white; }
.section-card { background: white; border-radius: 16px; padding: 1.5rem; box-shadow: var(--card-shadow); border: 1px solid rgba(0,0,0,0.04); }
.section-title { font-size: 0.875rem; font-weight: 700; color: var(--brand-800); margin-bottom: 1.25rem; display: flex; align-items: center; gap: 0.5rem; }
.section-title::before { content: ''; display: inline-block; width: 3px; height: 16px; background: var(--accent); border-radius: 2px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.25rem; }
.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field.full-width { grid-column: 1 / -1; }
.field label { font-size: 0.8rem; font-weight: 600; color: var(--brand-800); }
.field input, .field select { padding: 0.72rem 0.875rem; border: 1.5px solid var(--gray-200); border-radius: 10px; font-size: 0.875rem; outline: none; transition: all 0.18s; background: white; color: var(--text-primary); font-family: var(--font); }
.field input:focus, .field select:focus { border-color: var(--brand-500); box-shadow: 0 0 0 3px rgba(255,81,0,0.1); }
.btn-save { width: 100%; padding: 0.8rem; background: var(--brand-500); color: white; border: none; border-radius: 10px; font-size: 0.875rem; font-weight: 700; cursor: pointer; transition: all 0.18s; font-family: var(--font); }
.btn-save:hover:not(:disabled) { background: var(--brand-600); transform: translateY(-1px); }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }
.saved-badge { margin-top: 0.75rem; font-size: 0.82rem; color: #059669; font-weight: 600; }
.btn-create { width: 100%; padding: 1rem; background: var(--brand-500); color: white; border: none; border-radius: 12px; font-size: 1rem; font-weight: 700; cursor: pointer; box-shadow: 0 4px 16px rgba(255,81,0,0.3); transition: all 0.2s; font-family: var(--font); }
.btn-create:hover:not(:disabled) { background: var(--brand-600); transform: translateY(-1px); }
.btn-create:disabled { opacity: 0.6; cursor: not-allowed; }
@media (max-width: 768px) { .form-grid { grid-template-columns: 1fr; } .page-title { font-size: 1.3rem; } }
@media (max-width: 480px) { .section-card { padding: 1.25rem 1rem; } }
</style>
