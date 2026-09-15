<template>
  <div>
    <AppBreadcrumb :items="breadcrumbs" />
    <div class="page-head">
      <div>
        <h1 class="g-title">Edit Policy</h1>
        <p class="g-subtitle">Saving issues a new version of the documents and emails the driver the updated set.</p>
      </div>
    </div>

    <div v-if="toast.show" class="g-toast" :class="toast.type">{{ toast.message }}</div>
    <div v-if="loading" class="g-loading">Loading…</div>

    <div v-else class="form-wrap">

      <section class="g-section">
        <div class="g-section-title">Cover Period & Price</div>
        <div class="g-form-grid" style="margin-bottom:0;">
          <div class="g-field"><label>Start date (UK time) *</label><input v-model="policy.start_date" type="date" /></div>
          <div class="g-field"><label>Start time (UK time) *</label><input v-model="policy.start_time" type="time" /></div>
          <div class="g-field"><label>End date (UK time) *</label><input v-model="policy.end_date" type="date" /></div>
          <div class="g-field"><label>End time (UK time) *</label><input v-model="policy.end_time" type="time" /></div>
          <div class="g-field"><label>Price (£) *</label><input v-model="policy.price" type="number" step="0.01" min="0" /></div>
          <div class="g-field">
            <label>Cover type *</label>
            <select v-model="policy.cover_type">
              <option value="fully_comprehensive">Fully Comprehensive</option>
              <option value="third_party_fire_theft">Third Party, Fire & Theft</option>
              <option value="third_party_only">Third Party Only</option>
            </select>
          </div>
        </div>
      </section>

      <section class="g-section">
        <div class="g-section-title">Policy Holder</div>
        <div class="g-form-grid" style="margin-bottom:0;">
          <div class="g-field"><label>First name *</label><input v-model.trim="driver.first_name" type="text" /></div>
          <div class="g-field"><label>Last name *</label><input v-model.trim="driver.last_name" type="text" /></div>
          <div class="g-field"><label>Date of birth *</label><input v-model="driver.date_of_birth" type="date" /></div>
          <div class="g-field"><label>Sex *</label><select v-model="driver.sex"><option value="">Select…</option><option value="Male">Male</option><option value="Female">Female</option></select></div>
          <div class="g-field"><label>Driving licence no. *</label><input v-model.trim="driver.driving_licence" type="text" /></div>
          <div class="g-field"><label>Mobile *</label><input v-model.trim="driver.mobile" type="tel" /></div>
          <div class="g-field"><label>Email *</label><input v-model.trim="driver.email" type="email" /></div>
          <div class="g-field"><label>Address line 1 *</label><input v-model.trim="driver.address_line_1" type="text" /></div>
          <div class="g-field"><label>Address line 2</label><input v-model.trim="driver.address_line_2" type="text" /></div>
          <div class="g-field"><label>City *</label><input v-model.trim="driver.city" type="text" /></div>
          <div class="g-field"><label>Postcode *</label><input v-model.trim="driver.postcode" type="text" /></div>
          <div class="g-field full"><label>Occupation *</label><input v-model.trim="driver.occupation" type="text" /></div>
        </div>
      </section>

      <section class="g-section">
        <div class="g-section-title">Vehicle</div>
        <div class="g-form-grid" style="margin-bottom:0;">
          <div class="g-field"><label>Registration *</label><input v-model.trim="vehicle.registration" type="text" /></div>
          <div class="g-field"><label>Make *</label><input v-model.trim="vehicle.make" type="text" /></div>
          <div class="g-field"><label>Model *</label><input v-model.trim="vehicle.model" type="text" /></div>
          <div class="g-field"><label>Year *</label><input v-model="vehicle.year" type="number" /></div>
          <div class="g-field"><label>Colour</label><input v-model.trim="vehicle.color" type="text" /></div>
          <div class="g-field">
            <label>Vehicle value *</label>
            <select v-model="vehicle.value_range">
              <option value="£0-10000">£0 - £10,000</option>
              <option value="£10001-25000">£10,001 - £25,000</option>
              <option value="£25001-50000">£25,001 - £50,000</option>
              <option value="£50001-75000">£50,001 - £75,000</option>
              <option value="£75001-100000">£75,001 - £100,000</option>
              <option value="£100000+">£100,000+</option>
            </select>
          </div>
        </div>
      </section>

      <div class="form-actions">
        <NuxtLink :to="`/admin/policies/${route.params.id}`" class="g-btn g-btn-ghost">Cancel</NuxtLink>
        <button class="g-btn g-btn-primary save" @click="saveAll" :disabled="saving">{{ saving ? 'Saving…' : 'Save changes' }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'
import { splitDateTime } from '~/utils/format'

definePageMeta({ layout: 'admin' })
useHead({ title: 'Edit Policy' })

const auth = useAuthStore()
auth.init()
const route = useRoute()

const loading = ref(true)
const saving = ref(false)
const toast = ref({ show: false, message: '', type: 'success' })
const driverId = ref(null)
const vehicleId = ref(null)
const breadcrumbs = ref([
  { label: 'Policies', to: '/admin/policies' },
  { label: 'Policy', to: `/admin/policies/${route.params.id}` },
  { label: 'Edit' },
])

const policy  = ref({ start_date: '', start_time: '', end_date: '', end_time: '', price: '', cover_type: 'fully_comprehensive' })
const driver  = ref({ first_name: '', last_name: '', date_of_birth: '', driving_licence: '', mobile: '', email: '', address_line_1: '', address_line_2: '', city: '', postcode: '', occupation: '', sex: '' })
const vehicle = ref({ registration: '', make: '', model: '', year: '', color: '', value_range: '' })

function showToast(msg, type = 'success') {
  toast.value = { show: true, message: msg, type }
  setTimeout(() => (toast.value.show = false), 4000)
}

onMounted(async () => {
  try {
    const data = await api.get(`/api/policies/${route.params.id}`, auth.token)
    if (!['active', 'pending'].includes(data.policy.status)) {
      showToast(`This policy is ${data.policy.status} and cannot be edited`, 'error')
      setTimeout(() => navigateTo(`/admin/policies/${route.params.id}`), 1500)
      return
    }
    const s = splitDateTime(data.policy.start_datetime)
    const e = splitDateTime(data.policy.end_datetime)
    policy.value = { start_date: s.date, start_time: s.time, end_date: e.date, end_time: e.time, price: data.policy.price, cover_type: data.policy.cover_type }
    breadcrumbs.value = [
      { label: 'Policies', to: '/admin/policies' },
      { label: `Policy ${data.policy.policy_number}`, to: `/admin/policies/${route.params.id}` },
      { label: 'Edit' },
    ]
    driverId.value  = data.driver?.id  ?? data.policy.driver_id
    vehicleId.value = data.vehicle?.id ?? data.policy.vehicle_id
    if (data.driver) {
      const { id, ...d } = data.driver
      driver.value = { ...driver.value, ...d, address_line_2: d.address_line_2 || '' }
    }
    if (data.vehicle) {
      const { id, ...v } = data.vehicle
      vehicle.value = { ...vehicle.value, ...v, color: v.color || '' }
    }
  } catch (e) {
    showToast('Failed to load policy', 'error')
  } finally { loading.value = false }
})

async function saveAll() {
  if (!policy.value.start_date || !policy.value.end_date || !policy.value.price) { showToast('Fill in the cover period and price', 'error'); return }
  if (!driver.value.first_name || !driver.value.last_name) { showToast('Driver first and last name are required', 'error'); return }
  if (!vehicle.value.registration || !vehicle.value.make) { showToast('Vehicle registration and make are required', 'error'); return }
  const start = `${policy.value.start_date}T${policy.value.start_time || '00:00'}`
  const end   = `${policy.value.end_date}T${policy.value.end_time || '00:00'}`
  if (new Date(end) <= new Date(start)) { showToast('End must be after start', 'error'); return }

  saving.value = true
  try {
    await Promise.all([
      api.patch(`/api/policies/${route.params.id}`, {
        start_datetime: start, end_datetime: end,
        price: parseFloat(policy.value.price), cover_type: policy.value.cover_type,
      }, auth.token),
      api.patch(`/api/drivers/${driverId.value}`, { ...driver.value }, auth.token),
      api.patch(`/api/vehicles/${vehicleId.value}`, { ...vehicle.value, year: vehicle.value.year ? parseInt(vehicle.value.year) : undefined }, auth.token),
    ])
    showToast('Policy updated — new documents emailed to the driver')
    setTimeout(() => navigateTo(`/admin/policies/${route.params.id}`), 800)
  } catch (e) {
    showToast(e.message || 'Failed to save changes', 'error')
  } finally { saving.value = false }
}
</script>

<style scoped>
.page-head { margin-bottom: 1.5rem; }
.form-wrap { max-width: 820px; display: flex; flex-direction: column; gap: 1.25rem; }
.form-actions { display: flex; gap: 0.75rem; justify-content: flex-end; }
.save { min-width: 160px; }
@media (max-width: 640px) {
  .form-actions { flex-direction: column-reverse; }
  .form-actions .g-btn { width: 100%; }
}
</style>
