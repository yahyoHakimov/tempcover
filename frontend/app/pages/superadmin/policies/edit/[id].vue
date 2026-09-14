<template>
  <div>
    <AppBreadcrumb :items="breadcrumbs" />
    <h1 class="page-title">Edit Policy</h1>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else class="form-wrap">
      <div v-if="toast.show" class="toast" :class="toast.type">{{ toast.message }}</div>

      <!-- Policy Details -->
      <div class="card">
        <h2 class="card-title">Policy Details</h2>
        <div class="form-grid">
          <div class="field"><label>Start Date *</label><input v-model="policy.start_date" type="date" class="input" /></div>
          <div class="field"><label>Start Time *</label><input v-model="policy.start_time" type="time" class="input" /></div>
          <div class="field"><label>End Date *</label><input v-model="policy.end_date" type="date" class="input" /></div>
          <div class="field"><label>End Time *</label><input v-model="policy.end_time" type="time" class="input" /></div>
          <div class="field"><label>Price (£) *</label><input v-model="policy.price" type="number" step="0.01" min="0" class="input" /></div>
          <div class="field">
            <label>Cover Type *</label>
            <select v-model="policy.cover_type" class="input">
              <option value="fully_comprehensive">Fully Comprehensive</option>
              <option value="third_party_fire_theft">Third Party Fire & Theft</option>
              <option value="third_party_only">Third Party Only</option>
            </select>
          </div>
          <div class="field">
            <label>Status</label>
            <select v-model="policy.status" class="input">
              <option value="active">Active</option>
              <option value="expired">Expired</option>
              <option value="cancelled">Cancelled</option>
              <option value="pending">Pending</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Driver Details -->
      <div class="card">
        <h2 class="card-title">Policy Holder (Driver)</h2>
        <div class="form-grid">
          <div class="field"><label>First Name *</label><input v-model="driver.first_name" type="text" class="input" /></div>
          <div class="field"><label>Last Name *</label><input v-model="driver.last_name" type="text" class="input" /></div>
          <div class="field"><label>Date of Birth *</label><input v-model="driver.date_of_birth" type="date" class="input" /></div>
          <div class="field"><label>Sex *</label><select v-model="driver.sex" class="input"><option value="">Select…</option><option value="Male">Male</option><option value="Female">Female</option></select></div>
          <div class="field"><label>Driving Licence *</label><input v-model="driver.driving_licence" type="text" class="input" /></div>
          <div class="field"><label>Mobile *</label><input v-model="driver.mobile" type="tel" class="input" /></div>
          <div class="field"><label>Email *</label><input v-model="driver.email" type="email" class="input" /></div>
          <div class="field"><label>Address Line 1 *</label><input v-model="driver.address_line_1" type="text" class="input" /></div>
          <div class="field"><label>Address Line 2</label><input v-model="driver.address_line_2" type="text" class="input" /></div>
          <div class="field"><label>City *</label><input v-model="driver.city" type="text" class="input" /></div>
          <div class="field"><label>Postcode *</label><input v-model="driver.postcode" type="text" class="input" /></div>
          <div class="field full"><label>Occupation *</label><input v-model="driver.occupation" type="text" class="input" /></div>
        </div>
      </div>

      <!-- Vehicle Details -->
      <div class="card">
        <h2 class="card-title">Vehicle</h2>
        <div class="form-grid">
          <div class="field"><label>Registration *</label><input v-model="vehicle.registration" type="text" class="input" /></div>
          <div class="field"><label>Make *</label><input v-model="vehicle.make" type="text" class="input" /></div>
          <div class="field"><label>Model *</label><input v-model="vehicle.model" type="text" class="input" /></div>
          <div class="field"><label>Year *</label><input v-model="vehicle.year" type="number" class="input" /></div>
          <div class="field"><label>Color</label><input v-model="vehicle.color" type="text" class="input" /></div>
          <div class="field">
            <label>Vehicle Value *</label>
            <select v-model="vehicle.value_range" class="input">
              <option value="£0-10000">£0 - £10,000</option>
              <option value="£10001-25000">£10,001 - £25,000</option>
              <option value="£25001-50000">£25,001 - £50,000</option>
              <option value="£50001-75000">£50,001 - £75,000</option>
              <option value="£75001-100000">£75,001 - £100,000</option>
              <option value="£100000+">£100,000+</option>
            </select>
          </div>
        </div>
      </div>

      <button class="save-btn" @click="saveAll" :disabled="saving">
        {{ saving ? 'Saving...' : 'Save All Changes' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { splitDateTime } from '~/utils/format'
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'

definePageMeta({ layout: 'superadmin' })
const auth = useAuthStore()
auth.init()
const route = useRoute()

const loading = ref(true)
const saving = ref(false)
const toast = ref({ show: false, message: '', type: 'success' })

const driverId = ref(null)
const vehicleId = ref(null)
const breadcrumbs = ref([
  { label: 'Policies', to: '/superadmin/policies' },
  { label: 'Policy', to: `/superadmin/policies/${route.params.id}` },
  { label: 'Edit' },
])

const policy = ref({ start_date: '', start_time: '', end_date: '', end_time: '', price: '', cover_type: 'fully_comprehensive', status: 'active' })
const driver = ref({ first_name: '', last_name: '', date_of_birth: '', driving_licence: '', mobile: '', email: '', address_line_1: '', address_line_2: '', city: '', postcode: '', occupation: '', sex: '' })
const vehicle = ref({ registration: '', make: '', model: '', year: '', color: '', value_range: '' })

function showToast(msg, type = 'success') {
  toast.value = { show: true, message: msg, type }
  setTimeout(() => (toast.value.show = false), 4000)
}

// Vaqtlar UK zonasida (Europe/London) ko'rsatiladi — utils/format.ts bilan bir xil
const parseDatetime = splitDateTime

onMounted(async () => {
  try {
    const data = await api.get(`/api/superadmin/policies/${route.params.id}`, auth.token)

    const { date: sd, time: st } = parseDatetime(data.policy.start_datetime)
    const { date: ed, time: et } = parseDatetime(data.policy.end_datetime)

    policy.value = {
      start_date:  sd,
      start_time:  st,
      end_date:    ed,
      end_time:    et,
      price:       data.policy.price,
      cover_type:  data.policy.cover_type,
      status:      data.policy.status,
    }

    breadcrumbs.value = [
      { label: 'Policies', to: '/superadmin/policies' },
      { label: `Policy #${data.policy.policy_number}`, to: `/superadmin/policies/${route.params.id}` },
      { label: 'Edit' },
    ]

    driverId.value  = data.driver?.id  ?? data.policy.driver_id
    vehicleId.value = data.vehicle?.id ?? data.policy.vehicle_id

    if (data.driver) {
      driver.value = {
        first_name:      data.driver.first_name,
        last_name:       data.driver.last_name,
        date_of_birth:   data.driver.date_of_birth,
        driving_licence: data.driver.driving_licence,
        mobile:          data.driver.mobile,
        email:           data.driver.email,
        address_line_1:  data.driver.address_line_1,
        address_line_2:  data.driver.address_line_2 || '',
        city:            data.driver.city,
        postcode:        data.driver.postcode,
        occupation:      data.driver.occupation,
        sex:             data.driver.sex || '',
      }
    }

    if (data.vehicle) {
      vehicle.value = {
        registration: data.vehicle.registration,
        make:         data.vehicle.make,
        model:        data.vehicle.model,
        year:         data.vehicle.year,
        color:        data.vehicle.color || '',
        value_range:  data.vehicle.value_range,
      }
    }
  } catch (e) {
    showToast('Failed to load policy', 'error')
  } finally {
    loading.value = false
  }
})

async function saveAll() {
  if (!policy.value.start_date || !policy.value.end_date || !policy.value.price) {
    showToast('Fill all required policy fields', 'error')
    return
  }
  if (!driver.value.first_name || !driver.value.last_name) {
    showToast('Driver first and last name are required', 'error')
    return
  }
  if (!vehicle.value.registration || !vehicle.value.make) {
    showToast('Vehicle registration and make are required', 'error')
    return
  }

  saving.value = true
  try {
    await Promise.all([
      api.patch(`/api/superadmin/policies/${route.params.id}`, {
        start_datetime: `${policy.value.start_date}T${policy.value.start_time || '00:00'}`,
        end_datetime:   `${policy.value.end_date}T${policy.value.end_time || '00:00'}`,
        price:          parseFloat(policy.value.price),
        cover_type:     policy.value.cover_type,
        status:         policy.value.status,
      }, auth.token),

      api.patch(`/api/superadmin/drivers/${driverId.value}`, {
        ...driver.value,
      }, auth.token),

      api.patch(`/api/superadmin/vehicles/${vehicleId.value}`, {
        ...vehicle.value,
        year: vehicle.value.year ? parseInt(vehicle.value.year) : undefined,
      }, auth.token),
    ])

    showToast('Policy updated successfully!')
    setTimeout(() => navigateTo(`/superadmin/policies/${route.params.id}`), 1500)
  } catch (e) {
    showToast(e.message || 'Failed to save changes', 'error')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.back-link {
  color: #888; font-size: 0.85rem; text-decoration: none;
  display: inline-block; margin-bottom: 0.5rem;
}
.back-link:hover { color: var(--accent); }
.page-title { font-size: 1.6rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1.5rem; }

.loading { text-align: center; padding: 3rem; color: #888; }

.form-wrap { max-width: 780px; display: flex; flex-direction: column; gap: 1.25rem; }

.toast {
  padding: 0.875rem 1.25rem; border-radius: 10px;
  font-size: 0.875rem; font-weight: 500;
}
.toast.success { background: #e6f9f0; color: #00873a; border: 1px solid #b3f0d0; }
.toast.error   { background: #fff0f0; color: #cc0000; border: 1px solid #ffcccc; }

.card {
  background: white; border-radius: 16px;
  padding: 1.5rem; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.card-title { font-size: 1rem; font-weight: 700; color: var(--text-primary); margin-bottom: 1.25rem; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.field.full { grid-column: 1 / -1; }

.field label {
  font-size: 0.8rem; font-weight: 600;
  color: #555; display: block; margin-bottom: 0.4rem;
}

.input {
  padding: 0.72rem 0.875rem;
  border: 1.5px solid #e0e0e0;
  border-radius: 10px; font-size: 0.875rem;
  outline: none; transition: all 0.18s;
  background: white; color: var(--text-primary);
  font-family: var(--font); width: 100%;
}
.input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(255,81,0,0.1); }

.save-btn {
  width: 100%; padding: 1rem;
  background: var(--brand-500);
  color: white; border: none; border-radius: 12px;
  font-size: 1rem; font-weight: 700; cursor: pointer;
  transition: all 0.2s; font-family: var(--font);
  box-shadow: 0 4px 16px rgba(255,81,0,0.3);
}
.save-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.save-btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

@media (max-width: 480px) {
  .form-grid { grid-template-columns: 1fr; }
  .field.full { grid-column: 1; }
  .save-btn { font-size: 0.95rem; }
}
</style>
