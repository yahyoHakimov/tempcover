<template><div class="g-loading">Redirecting…</div></template>
<script setup>
// Legacy route: the driver documents page now lives at /verifydetailspolicy/complete/<policy number>
definePageMeta({ layout: false })
onMounted(() => {
  try {
    const d = JSON.parse(localStorage.getItem('driver_portal_data') || 'null')
    if (d?.policy?.policy_number) return navigateTo(`/verifydetailspolicy/complete/${encodeURIComponent(d.policy.policy_number)}`, { replace: true })
  } catch {}
  navigateTo('/verifydetailspolicy', { replace: true })
})
</script>
