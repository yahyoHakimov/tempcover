<template>
  <div class="g-loading">Redirecting…</div>
</template>

<script setup>
// /admin -> /admin/dashboard/<username> (handled by the global middleware; this is the fallback)
import { useAuthStore } from '~/stores/auth'
definePageMeta({ layout: false })
const auth = useAuthStore()
onMounted(() => { auth.init(); navigateTo(auth.isLoggedIn ? auth.homePath : '/admin/login', { replace: true }) })
</script>
