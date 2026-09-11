<template>
  <div class="tc-shell">
    <AppTopbar :links="links" home-to="/superadmin" role-label="Super Admin" :user-name="auth.name || ''" @signout="auth.logout()" />
    <main class="tc-main">
      <slot />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
auth.init()

const links = [
  { to: '/superadmin',          label: 'Dashboard', exact: true },
  { to: '/superadmin/tenants',  label: 'Agents' },
  { to: '/superadmin/policies', label: 'Policies' },
  { to: '/superadmin/drivers',  label: 'Drivers' },
  { to: '/superadmin/settings', label: 'Settings' },
]
</script>
