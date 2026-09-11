<template>
  <div class="driver-page">
    <header class="header">
      <img src="/tempcover-logo-white.png" alt="TempCover" class="header-logo" />
    </header>

    <div class="container">
      <div class="card">
        <h1 class="title">Access your policy</h1>
        <p class="desc">Enter your details to view and download your insurance documents.</p>

        <div v-if="error" class="error-box" role="alert">{{ error }}</div>

        <form @submit.prevent="handleLogin" novalidate>
          <div class="field">
            <label for="pn">Policy number</label>
            <input id="pn" v-model.trim="form.policy_number" type="text" inputmode="numeric" placeholder="e.g. 12345678" autocomplete="off" />
          </div>
          <div class="field">
            <label for="ln">Last name</label>
            <input id="ln" v-model.trim="form.last_name" type="text" placeholder="Smith" autocomplete="family-name" />
          </div>
          <div class="field">
            <label for="dob">Date of birth</label>
            <input id="dob" v-model="form.date_of_birth" type="date" autocomplete="bday" />
          </div>

          <button type="submit" class="btn" :disabled="loading">
            <span v-if="loading">Checking your details…</span>
            <span v-else>Access my documents</span>
          </button>
        </form>

        <p class="hint">Your policy number is in your confirmation email.</p>
      </div>

      <p class="foot">
        <NuxtLink to="/terms">Terms</NuxtLink> · <NuxtLink to="/privacy">Privacy</NuxtLink> · <NuxtLink to="/contact">Contact</NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { api } from '~/utils/api'

definePageMeta({ layout: false })
useHead({ title: 'My Insurance' })

const form = ref({ policy_number: '', last_name: '', date_of_birth: '' })
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  if (!form.value.policy_number || !form.value.last_name || !form.value.date_of_birth) {
    error.value = 'Please fill in all three fields.'
    return
  }
  loading.value = true
  try {
    const data = await api.post('/api/drivers/portal/login', {
      policy_number: form.value.policy_number.toUpperCase(),
      last_name:     form.value.last_name,
      date_of_birth: form.value.date_of_birth,
    })
    localStorage.setItem('driver_portal_data', JSON.stringify(data))
    navigateTo('/driver/portal')
  } catch (e) {
    error.value = /cancelled/i.test(e.message)
      ? 'This policy has been cancelled. Please contact us if you need help.'
      : 'The details you entered do not match our records. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.driver-page { min-height: 100vh; background: var(--main-bg); font-family: var(--font); display: flex; flex-direction: column; }
.header { background: var(--brand-500); height: var(--topbar-h); display: flex; align-items: center; padding: 0 1.5rem; box-shadow: 0 2px 8px rgba(255,81,0,0.25); }
.header-logo { height: 26px; }

.container { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2.5rem 1rem; }
.card { background: white; border-radius: 16px; padding: 2.5rem; width: 100%; max-width: 460px; border: 1px solid var(--card-border); box-shadow: 0 8px 40px rgba(17,24,39,0.08); }

.title { font-size: 1.6rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.4rem; }
.desc { font-size: 0.9rem; color: var(--text-muted); margin-bottom: 1.75rem; line-height: 1.5; }

.error-box { background: var(--error-bg); border: 1px solid var(--error-border); color: var(--error); padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.85rem; margin-bottom: 1.25rem; }

.field { display: flex; flex-direction: column; gap: 0.45rem; margin-bottom: 1.1rem; }
.field label { font-size: 0.875rem; font-weight: 500; color: var(--text-primary); }
.field input {
  padding: 0.9rem 1rem; border: 1.5px solid var(--gray-300); border-radius: 8px; font-size: 1rem;
  outline: none; transition: all 0.18s; background: white; color: var(--text-primary); font-family: inherit; width: 100%;
}
.field input:focus { border-color: var(--brand-500); box-shadow: 0 0 0 4px rgba(255,81,0,0.10); }

.btn {
  width: 100%; height: 58px; margin-top: 0.5rem; background: var(--brand-500); color: white; border: none; border-radius: 8px;
  font-size: 1.05rem; font-weight: 700; cursor: pointer; transition: all 0.2s; font-family: inherit;
}
.btn:hover:not(:disabled) { background: var(--brand-600); transform: translateY(-1px); box-shadow: 0 6px 18px rgba(255,81,0,0.3); }
.btn:disabled { opacity: 0.7; cursor: not-allowed; }

.hint { text-align: center; font-size: 0.78rem; color: var(--text-muted); margin-top: 1.1rem; }
.foot { margin-top: 1.5rem; font-size: 0.8rem; color: var(--text-muted); }
.foot a { color: var(--text-muted); text-decoration: none; }
.foot a:hover { color: var(--brand-600); }

@media (max-width: 480px) { .card { padding: 1.75rem 1.25rem; } }
</style>
