<template><div></div></template>
<script setup>
// Legacy document link — drivers now sign in with policy number, surname and date of birth.
definePageMeta({ layout: false })
onMounted(() => navigateTo('/verifydetailspolicy', { replace: true }))
</script>
