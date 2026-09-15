<template><div /></template>

<script setup>
// Eski manzil: haydovchi kirish sahifasi endi /verifydetailspolicy (asl Tempcover yo'li)
definePageMeta({ layout: false })
const route = useRoute()
onMounted(() => navigateTo({ path: '/verifydetailspolicy', query: route.query }, { replace: true }))
</script>
