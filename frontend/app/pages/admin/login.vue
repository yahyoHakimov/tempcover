<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-logo">
        <img src="/tempcover-logo.png" alt="TempCover" />
      </div>

      <h1 class="login-title">Admin</h1>
      <p class="login-desc">Admin Portal</p>

      <form @submit.prevent="handleLogin" novalidate>
        <div v-if="error" class="error-box" role="alert">{{ error }}</div>

        <div class="field">
          <label for="username">Username</label>
          <input id="username" v-model.trim="username" type="text" autocomplete="username" :disabled="loading" required />
        </div>

        <div class="field">
          <label for="password">Password</label>
          <div class="password-wrap">
            <input id="password" v-model="password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" :disabled="loading" required />
            <button type="button" class="eye-btn" :aria-label="showPassword ? 'Hide password' : 'Show password'" @click="showPassword = !showPassword">
              <svg v-if="!showPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            </button>
          </div>
        </div>

        <button type="submit" class="login-btn" :disabled="loading">
          <span v-if="loading" class="spinner" aria-hidden="true"></span>
          <span v-else>Sign in</span>
        </button>
      </form>

      <p class="login-footer">Admin Portal - Authorized Personnel Only</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: false })
useHead({ title: 'Admin Login' })

const auth = useAuthStore()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const showPassword = ref(false)

const route = useRoute()
onMounted(() => {
  if (route.query.reason === 'expired') error.value = 'Your session has expired. Please contact the administrator or sign in again.'
})

async function handleLogin() {
  error.value = ''
  if (!username.value || !password.value) {
    error.value = 'Please enter your username and password.'
    return
  }
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    await navigateTo(auth.homePath)
  } catch (e) {
    error.value = e.message || 'Invalid username or password'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: #FAFAFA;
  display: flex; align-items: center; justify-content: center;
  padding: 2rem 1rem;
  font-family: var(--font);
}
.login-card {
  background: white; border-radius: 16px;
  padding: 3.5rem 2.25rem 2.25rem;
  width: 100%; max-width: 505px;
  box-shadow: 0 8px 40px rgba(17,24,39,0.10);
}
.login-logo { text-align: center; margin-bottom: 3.5rem; }
.login-logo img { height: 36px; width: auto; }

.login-title { font-size: 2.25rem; font-weight: 700; color: var(--text-primary); text-align: center; margin-bottom: 0.4rem; letter-spacing: -0.3px; }
.login-desc { font-size: 1.15rem; color: var(--text-muted); text-align: center; margin-bottom: 2.5rem; }

.error-box {
  background: var(--error-bg); border: 1px solid var(--error-border); color: var(--error);
  padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.875rem; margin-bottom: 1.25rem;
}

.field { display: flex; flex-direction: column; gap: 0.6rem; margin-bottom: 1.5rem; }
.field label { font-size: 0.95rem; font-weight: 500; color: var(--text-primary); }
.field input {
  width: 100%; height: 62px; padding: 0 1.1rem;
  border: 1.5px solid var(--gray-300); border-radius: 8px;
  font-size: 1.05rem; color: var(--text-primary); background: white;
  outline: none; transition: border-color 0.18s, box-shadow 0.18s; font-family: inherit;
}
.field input:hover { border-color: var(--brand-400); }
.field input:focus { border-color: var(--brand-500); box-shadow: 0 0 0 4px rgba(255,81,0,0.10); }
.field input:disabled { opacity: 0.6; }

.password-wrap { position: relative; }
.password-wrap input { padding-right: 3.25rem; }
.eye-btn {
  position: absolute; right: 0.85rem; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer; color: var(--gray-400); padding: 0.25rem; display: flex;
}
.eye-btn:hover { color: var(--brand-500); }

.login-btn {
  width: 100%; height: 64px; margin-top: 0.5rem;
  background: var(--brand-500); color: white; border: none; border-radius: 8px;
  font-size: 1.15rem; font-weight: 700; cursor: pointer;
  transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
  display: flex; align-items: center; justify-content: center; font-family: inherit;
}
.login-btn:hover:not(:disabled) { background: var(--brand-600); box-shadow: 0 6px 18px rgba(255,81,0,0.3); transform: translateY(-1px); }
.login-btn:disabled { opacity: 0.7; cursor: not-allowed; }

.spinner { width: 20px; height: 20px; border: 2.5px solid rgba(255,255,255,0.35); border-top-color: white; border-radius: 50%; animation: spin 0.7s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }

.login-footer { text-align: center; font-size: 0.8rem; color: var(--text-muted); margin-top: 2rem; }

@media (max-width: 520px) {
  .login-card { padding: 2.5rem 1.5rem 1.75rem; }
  .login-logo { margin-bottom: 2.5rem; }
  .login-title { font-size: 1.9rem; }
  .field input, .login-btn { height: 56px; }
}
</style>
