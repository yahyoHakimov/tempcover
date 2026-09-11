<template>
  <div>
    <AppBreadcrumb :items="[{ label: 'Policies', to: '/admin/policies' }, { label: 'Create Policy' }]" />

    <div class="page-head">
      <div>
        <h1 class="g-title">Create Policy</h1>
        <p class="g-subtitle">Issue a new short-term policy. The driver receives their documents by email.</p>
      </div>
    </div>

    <div v-if="toast.show" class="g-toast" :class="toast.type">{{ toast.message }}</div>

    <div class="form-wrap">

      <!-- Step 1: Driver -->
      <section class="g-section">
        <div class="step-head">
          <span class="step-num" :class="{ done: selectedDriverId }">1</span>
          <div class="g-section-title" style="margin:0;">Policy Holder</div>
          <span v-if="selectedDriverId" class="step-done">Driver ready</span>
        </div>

        <div class="g-field" style="margin-bottom:1rem;">
          <label>Load a saved driver</label>
          <AppSearchSelect
            v-model="selectedDriverObj"
            :options="savedDrivers"
            :get-label="d => `${d.first_name} ${d.last_name} · ${d.email}`"
            placeholder="Search or select a saved driver…"
            removable
            @select="loadDriver"
            @remove="deleteDriver"
          />
        </div>

        <div class="g-form-grid">
          <div class="g-field"><label>First name *</label><input v-model.trim="driver.first_name" type="text" placeholder="John" /></div>
          <div class="g-field"><label>Last name *</label><input v-model.trim="driver.last_name" type="text" placeholder="Smith" /></div>
          <div class="g-field"><label>Date of birth *</label><input v-model="driver.date_of_birth" type="date" /></div>
          <div class="g-field"><label>Driving licence no. *</label><input v-model.trim="driver.driving_licence" type="text" placeholder="SMITH901201AB9CD" /></div>
          <div class="g-field"><label>Mobile *</label><input v-model.trim="driver.mobile" type="tel" placeholder="+44 7700 900000" /></div>
          <div class="g-field"><label>Email *</label><input v-model.trim="driver.email" type="email" placeholder="john@example.com" /></div>
          <div class="g-field"><label>Address line 1 *</label><input v-model.trim="driver.address_line_1" type="text" /></div>
          <div class="g-field"><label>Address line 2</label><input v-model.trim="driver.address_line_2" type="text" /></div>
          <div class="g-field"><label>City *</label><input v-model.trim="driver.city" type="text" /></div>
          <div class="g-field"><label>Postcode *</label><input v-model.trim="driver.postcode" type="text" /></div>
          <div class="g-field full"><label>Occupation *</label><input v-model.trim="driver.occupation" type="text" /></div>
        </div>

        <div class="section-actions">
          <button class="g-btn g-btn-primary" @click="saveDriver" :disabled="savingDriver">
            {{ savingDriver ? 'Saving…' : (selectedDriverId ? 'Save as new driver' : 'Save driver') }}
          </button>
          <button v-if="selectedDriverId" class="g-btn g-btn-ghost" @click="clearDriver">Clear</button>
        </div>
      </section>

      <!-- Step 2: Vehicle -->
      <section class="g-section">
        <div class="step-head">
          <span class="step-num" :class="{ done: selectedVehicleId }">2</span>
          <div class="g-section-title" style="margin:0;">Vehicle</div>
          <span v-if="selectedVehicleId" class="step-done">Vehicle ready</span>
        </div>

        <div class="g-field" style="margin-bottom:1rem;">
          <label>Load a saved vehicle</label>
          <AppSearchSelect
            v-model="selectedVehicleObj"
            :options="savedVehicles"
            :get-label="v => `${v.registration} — ${v.make} ${v.model}`"
            placeholder="Search or select a saved vehicle…"
            @select="loadVehicle"
          />
        </div>

        <div class="g-form-grid">
          <div class="g-field"><label>Registration *</label><input v-model.trim="vehicle.registration" type="text" placeholder="AB12 CDE" class="upper" /></div>
          <div class="g-field"><label>Make *</label><input v-model.trim="vehicle.make" type="text" placeholder="FORD" /></div>
          <div class="g-field"><label>Model *</label><input v-model.trim="vehicle.model" type="text" placeholder="FOCUS" /></div>
          <div class="g-field"><label>Year *</label><input v-model="vehicle.year" type="number" min="1950" max="2100" placeholder="2022" /></div>
          <div class="g-field">
            <label>Vehicle value *</label>
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
          <div class="g-field"><label>Colour</label><input v-model.trim="vehicle.color" type="text" placeholder="White" /></div>
        </div>

        <div class="section-actions">
          <button class="g-btn g-btn-primary" @click="saveVehicle" :disabled="savingVehicle">
            {{ savingVehicle ? 'Saving…' : (selectedVehicleId ? 'Save as new vehicle' : 'Save vehicle') }}
          </button>
          <button v-if="selectedVehicleId" class="g-btn g-btn-ghost" @click="clearVehicle">Clear</button>
        </div>
      </section>

      <!-- Step 3: Cover -->
      <section class="g-section">
        <div class="step-head">
          <span class="step-num">3</span>
          <div class="g-section-title" style="margin:0;">Cover Period & Price</div>
        </div>

        <div class="g-form-grid">
          <div class="g-field"><label>Start date *</label><input v-model="policy.start_date" type="date" /></div>
          <div class="g-field"><label>Start time *</label><input v-model="policy.start_time" type="time" /></div>
          <div class="g-field"><label>End date *</label><input v-model="policy.end_date" type="date" /></div>
          <div class="g-field"><label>End time *</label><input v-model="policy.end_time" type="time" /></div>
        </div>

        <div class="durations">
          <span class="durations-label">Quick duration</span>
          <button v-for="d in DURATIONS" :key="d.label" type="button" class="chip" @click="applyDuration(d)">{{ d.label }}</button>
        </div>

        <div class="g-form-grid" style="margin-top:1.25rem;margin-bottom:0;">
          <div class="g-field">
            <label>Cover type</label>
            <select v-model="policy.cover_type">
              <option value="fully_comprehensive">Fully Comprehensive</option>
              <option value="third_party_fire_theft">Third Party, Fire & Theft</option>
              <option value="third_party_only">Third Party Only</option>
            </select>
          </div>
          <div class="g-field"><label>Price (£) *</label><input v-model="policy.price" type="number" step="0.01" min="0" placeholder="0.00" /></div>
        </div>
      </section>

      <div class="summary" v-if="summaryText">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        <span>{{ summaryText }}</span>
      </div>

      <button class="create-btn" @click="createPolicy" :disabled="creating">
        <svg v-if="!creating" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        <span>{{ creating ? 'Creating policy…' : 'Create Policy' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'

definePageMeta({ layout: 'admin' })
useHead({ title: 'Create Policy' })

const auth = useAuthStore()
auth.init()

const DURATIONS = [
  { label: '1 hour',  hours: 1 },
  { label: '3 hours', hours: 3 },
  { label: '1 day',   hours: 24 },
  { label: '3 days',  hours: 72 },
  { label: '7 days',  hours: 24 * 7 },
  { label: '28 days', hours: 24 * 28 },
]

const savedDrivers  = ref([])
const savedVehicles = ref([])
const savingDriver  = ref(false)
const savingVehicle = ref(false)
const creating      = ref(false)
const selectedDriverId  = ref(null)
const selectedVehicleId = ref(null)
const selectedDriverObj  = ref(null)
const selectedVehicleObj = ref(null)
const toast = ref({ show: false, message: '', type: 'success' })

const emptyDriver  = () => ({ first_name:'', last_name:'', date_of_birth:'', driving_licence:'', mobile:'', email:'', address_line_1:'', address_line_2:'', city:'', postcode:'', occupation:'' })
const emptyVehicle = () => ({ registration:'', make:'', model:'', year:'', color:'', value_range:'' })

const driver  = ref(emptyDriver())
const vehicle = ref(emptyVehicle())
const policy  = ref({ start_date:'', start_time:'', end_date:'', end_time:'', price:'', cover_type:'fully_comprehensive' })

function showToast(msg, type = 'success') {
  toast.value = { show: true, message: msg, type }
  setTimeout(() => (toast.value.show = false), 3500)
}

const summaryText = computed(() => {
  const s = policy.value.start_date && `${policy.value.start_date}T${policy.value.start_time || '00:00'}`
  const e = policy.value.end_date && `${policy.value.end_date}T${policy.value.end_time || '00:00'}`
  if (!s || !e) return ''
  const ms = new Date(e) - new Date(s)
  if (isNaN(ms)) return ''
  if (ms <= 0) return 'End must be after start.'
  const h = Math.round(ms / 3600000)
  const dur = h < 24 ? `${h} hour${h === 1 ? '' : 's'}` : `${Math.floor(h / 24)} day${Math.floor(h / 24) === 1 ? '' : 's'}${h % 24 ? ` ${h % 24}h` : ''}`
  return `Cover runs for ${dur}${policy.value.price ? ` · £${Number(policy.value.price).toFixed(2)}` : ''}`
})

function pad(n) { return String(n).padStart(2, '0') }

function applyDuration(d) {
  // Default the start to now (rounded to the next 5 minutes) when it is empty
  if (!policy.value.start_date || !policy.value.start_time) {
    const now = new Date()
    now.setMinutes(Math.ceil(now.getMinutes() / 5) * 5, 0, 0)
    policy.value.start_date = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
    policy.value.start_time = `${pad(now.getHours())}:${pad(now.getMinutes())}`
  }
  const start = new Date(`${policy.value.start_date}T${policy.value.start_time}`)
  const end = new Date(start.getTime() + d.hours * 3600000)
  policy.value.end_date = `${end.getFullYear()}-${pad(end.getMonth() + 1)}-${pad(end.getDate())}`
  policy.value.end_time = `${pad(end.getHours())}:${pad(end.getMinutes())}`
}

async function loadSavedData() {
  try {
    const [d, v] = await Promise.all([api.get('/api/drivers/', auth.token), api.get('/api/vehicles/', auth.token)])
    savedDrivers.value  = d
    savedVehicles.value = v
  } catch (e) { console.error(e) }
}

function loadDriver(d) {
  if (!d) return
  driver.value = { ...emptyDriver(), ...d }
  selectedDriverId.value = d.id
}
function clearDriver() {
  driver.value = emptyDriver()
  selectedDriverId.value = null
  selectedDriverObj.value = null
}
function loadVehicle(v) {
  if (!v) return
  vehicle.value = { ...emptyVehicle(), ...v }
  selectedVehicleId.value = v.id
}
function clearVehicle() {
  vehicle.value = emptyVehicle()
  selectedVehicleId.value = null
  selectedVehicleObj.value = null
}

const REQUIRED_DRIVER = ['first_name', 'last_name', 'date_of_birth', 'driving_licence', 'mobile', 'email', 'address_line_1', 'city', 'postcode', 'occupation']

async function saveDriver() {
  const missing = REQUIRED_DRIVER.filter(k => !driver.value[k])
  if (missing.length) { showToast('Please complete all required driver fields', 'error'); return }
  savingDriver.value = true
  try {
    const { id, policy_count, active_policy_count, last_policy_at, ...payload } = driver.value
    const saved = await api.post('/api/drivers/', payload, auth.token)
    selectedDriverId.value = saved.id
    selectedDriverObj.value = saved
    savedDrivers.value.push(saved)
    showToast('Driver saved')
  } catch (e) { showToast(e.message, 'error') }
  finally { savingDriver.value = false }
}

async function deleteDriver(d) {
  if (!confirm(`Delete driver ${d.first_name} ${d.last_name}? Their old (cancelled/expired) policy records will also be removed.`)) return
  try {
    await api.delete(`/api/drivers/${d.id}`, auth.token)
    savedDrivers.value = savedDrivers.value.filter(x => x.id !== d.id)
    if (selectedDriverId.value === d.id) clearDriver()
    showToast('Driver deleted')
  } catch (e) { showToast(e.message, 'error') }
}

async function saveVehicle() {
  if (!vehicle.value.registration || !vehicle.value.make || !vehicle.value.model || !vehicle.value.year || !vehicle.value.value_range) {
    showToast('Please complete all required vehicle fields', 'error'); return
  }
  savingVehicle.value = true
  try {
    const { id, ...payload } = vehicle.value
    const saved = await api.post('/api/vehicles/', { ...payload, year: parseInt(vehicle.value.year) }, auth.token)
    selectedVehicleId.value = saved.id
    selectedVehicleObj.value = saved
    savedVehicles.value.push(saved)
    showToast('Vehicle saved')
  } catch (e) { showToast(e.message, 'error') }
  finally { savingVehicle.value = false }
}

async function createPolicy() {
  if (!selectedDriverId.value)  { showToast('Save or load a driver first (step 1)', 'error'); return }
  if (!selectedVehicleId.value) { showToast('Save or load a vehicle first (step 2)', 'error'); return }
  if (!policy.value.start_date || !policy.value.end_date || !policy.value.price) { showToast('Fill in the cover period and price', 'error'); return }
  const start = `${policy.value.start_date}T${policy.value.start_time || '00:00'}`
  const end   = `${policy.value.end_date}T${policy.value.end_time || '00:00'}`
  if (new Date(end) <= new Date(start)) { showToast('End must be after start', 'error'); return }

  creating.value = true
  try {
    const created = await api.post('/api/policies/', {
      driver_id:      selectedDriverId.value,
      vehicle_id:     selectedVehicleId.value,
      start_datetime: start,
      end_datetime:   end,
      price:          parseFloat(policy.value.price),
      cover_type:     policy.value.cover_type,
    }, auth.token)
    showToast(`Policy ${created.policy_number} created`)
    setTimeout(() => navigateTo(`/admin/policies/${created.id}`), 900)
  } catch (e) { showToast(e.message, 'error') }
  finally { creating.value = false }
}

onMounted(loadSavedData)
</script>

<style scoped>
.page-head { margin-bottom: 1.5rem; }
.form-wrap { max-width: 820px; display: flex; flex-direction: column; gap: 1.25rem; }

.step-head { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; }
.step-num {
  width: 28px; height: 28px; border-radius: 50%; background: var(--gray-100); color: var(--text-secondary);
  display: inline-flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 700; flex-shrink: 0;
}
.step-num.done { background: var(--success-bg); color: var(--success); }
.step-head .g-section-title::before { display: none; }
.step-done { margin-left: auto; font-size: 0.78rem; font-weight: 600; color: var(--success); }

.upper { text-transform: uppercase; }
.section-actions { display: flex; gap: 0.6rem; flex-wrap: wrap; }

.durations { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.durations-label { font-size: 0.78rem; color: var(--text-muted); margin-right: 0.25rem; }

.summary {
  display: flex; align-items: center; gap: 0.6rem; padding: 0.85rem 1rem;
  background: var(--brand-50); border: 1px solid var(--brand-200); border-radius: 10px;
  color: var(--brand-700); font-size: 0.875rem; font-weight: 500;
}

.create-btn {
  display: flex; align-items: center; justify-content: center; gap: 0.6rem;
  width: 100%; height: 64px; background: var(--brand-500); color: white; border: none; border-radius: 10px;
  font-size: 1.1rem; font-weight: 500; cursor: pointer; transition: background 0.2s, transform 0.15s, box-shadow 0.2s; font-family: var(--font);
}
.create-btn:hover:not(:disabled) { background: var(--brand-600); transform: translateY(-1px); box-shadow: 0 8px 22px rgba(255,81,0,0.30); }
.create-btn:disabled { opacity: 0.65; cursor: not-allowed; }

@media (max-width: 640px) {
  .section-actions .g-btn { width: 100%; }
}
</style>
