<template>
  <div class="countdown" :class="{ expired: isExpired, none: !expiresAt }" aria-live="polite">
    <template v-if="!expiresAt">
      <p class="cd-note">Your access has no expiry date.</p>
    </template>
    <template v-else-if="isExpired">
      <p class="cd-note expired-note">Your session has expired. Please contact the administrator.</p>
    </template>
    <template v-else>
      <div class="cd-unit"><span class="cd-value">{{ parts.days }}</span><span class="cd-label">Days</span></div>
      <div class="cd-unit"><span class="cd-value">{{ parts.hours }}</span><span class="cd-label">Hours</span></div>
      <div class="cd-unit"><span class="cd-value">{{ parts.minutes }}</span><span class="cd-label">Minutes</span></div>
      <div class="cd-unit"><span class="cd-value">{{ parts.seconds }}</span><span class="cd-label">Seconds</span></div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  expiresAt: { type: String, default: null },   // ISO datetime
})

const now = ref(Date.now())
let timer = null

const remainingMs = computed(() => {
  if (!props.expiresAt) return 0
  return new Date(props.expiresAt).getTime() - now.value
})
const isExpired = computed(() => !!props.expiresAt && remainingMs.value <= 0)

const parts = computed(() => {
  const total = Math.max(0, Math.floor(remainingMs.value / 1000))
  return {
    days:    Math.floor(total / 86400),
    hours:   Math.floor((total % 86400) / 3600),
    minutes: Math.floor((total % 3600) / 60),
    seconds: total % 60,
  }
})

function start() {
  stop()
  if (props.expiresAt) timer = setInterval(() => { now.value = Date.now() }, 1000)
}
function stop() { if (timer) { clearInterval(timer); timer = null } }

onMounted(start)
onUnmounted(stop)
watch(() => props.expiresAt, start)
</script>

<style scoped>
.countdown { display: flex; justify-content: center; align-items: flex-start; gap: 2.5rem; flex-wrap: wrap; }
.cd-unit { display: flex; flex-direction: column; align-items: center; min-width: 56px; }
.cd-value { font-size: 2.4rem; font-weight: 700; color: var(--brand-500); line-height: 1.1; font-variant-numeric: tabular-nums; }
.cd-label { font-size: 0.9rem; color: var(--text-muted); margin-top: 0.35rem; }
.cd-note { color: var(--text-muted); font-size: 0.95rem; text-align: center; }
.expired-note { color: var(--error); font-weight: 500; }
@media (max-width: 480px) {
  .countdown { gap: 1.25rem; }
  .cd-value { font-size: 1.9rem; }
  .cd-label { font-size: 0.8rem; }
}
</style>
