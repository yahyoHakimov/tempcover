<template>
  <div class="tc-shell">
    <AppTopbar :links="links" :home-to="auth.homePath" :user-name="auth.name || ''" @signout="auth.logout()" />
    <main class="tc-main">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
auth.init()

const links = computed(() => [
  { to: auth.homePath,      label: 'Dashboard', match: '/admin/dashboard' },
  { to: '/admin/policies',  label: 'Policies' },
  { to: '/admin/drivers',   label: 'Drivers' },
])
</script>
