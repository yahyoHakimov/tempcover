<template>
  <div class="docs-page">
    <header class="bar">
      <NuxtLink to="/verifydetailspolicy" aria-label="Home"><img src="/tempcover-logo-white.png" alt="TempCover" class="bar-logo" /></NuxtLink>
    </header>

    <main class="wrap">
      <h1 class="h1">Short term insurance</h1>
      <p class="lede">Temporary and short term vehicle insurance, from 1 hour to 28 days.</p>

      <div v-if="loading" class="loading">Loading your policy…</div>

      <template v-else-if="error">
        <div class="error-card">
          <h2 class="h2">Policy documents</h2>
          <p class="error-text">{{ error }}</p>
          <NuxtLink :to="`/verifydetailspolicy?ref=${encodeURIComponent(policyRef)}`" class="btn-home">Sign in with your details</NuxtLink>
        </div>
      </template>

      <template v-else-if="data">
        <h2 class="h2">Policy details</h2>

        <div class="details">
          <div class="row">
            <div><span class="lbl">FROM</span> {{ data.policy.start_datetime }}</div>
            <div><span class="lbl">TO</span> {{ data.policy.end_datetime }}</div>
          </div>
          <div class="row">Your reference: <strong>{{ data.policy.policy_number }}</strong></div>
          <div class="row"><strong>Policy: {{ data.policy.cover_label }} cover</strong></div>
          <div v-if="data.policy.version > 1" class="row small">Documents version {{ data.policy.version }} (re-issued after a policy change)</div>
        </div>

        <div v-if="status === 'pending'" class="notice info">Your cover has not started yet. It begins on {{ data.policy.start_datetime }}.</div>
        <div v-else-if="status === 'expired'" class="notice warn">This policy has expired. The documents remain available for your records.</div>

        <section class="panel">
          <div class="panel-head">Documents you need now</div>
          <div class="panel-body">
            <p class="panel-note">
              Your policy documents are listed below and have also been sent to the email address provided.
              If you need your documents posted to you, please let us know by emailing
              <a :href="`mailto:${data.support_email}`">{{ data.support_email }}</a>.
            </p>
            <ul class="doc-list">
              <li v-for="doc in data.documents" :key="doc.name">
                <a :href="doc.url" target="_blank" rel="noopener" class="doc-link">
                  <span class="pdf-icon" aria-hidden="true">
                    <svg width="22" height="26" viewBox="0 0 22 26"><path d="M2 0h12l6 6v18a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2z" fill="#D93025"/><path d="M14 0v6h6" fill="#F28B82"/><text x="11" y="19" text-anchor="middle" font-size="7" font-weight="700" fill="#fff" font-family="Arial">PDF</text></svg>
                  </span>
                  <span>{{ doc.name }}</span>
                </a>
              </li>
            </ul>
          </div>
        </section>

        <a href="https://www.tempcover.com/hp-new/bk-new" class="btn-home">Home</a>
      </template>
    </main>

    <footer class="foot">
      <NuxtLink to="/terms">Terms</NuxtLink> · <NuxtLink to="/privacy">Privacy</NuxtLink> · <NuxtLink to="/contact">Contact</NuxtLink>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

definePageMeta({ layout: false })
useHead({ title: 'Policy documents' })

const route = useRoute()
const policyRef = String(route.params.ref || '')

const data = ref(null)
const loading = ref(true)
const error = ref('')

const status = computed(() => (data.value?.policy?.status || '').toLowerCase())

onMounted(async () => {
  try {
    // Hujjatlar faqat kirishdan keyin (polis raqami + familiya + tug'ilgan sana).
    // Emaildagi tugma /verifydetailspolicy?ref=... ga olib keladi; eski xatlardagi ?t= havolalar
    // ham shu yerga yo'naltiriladi — token bilan so'roqsiz ochish yo'q.
    const stored = localStorage.getItem('driver_portal_data')
    const parsed = stored ? JSON.parse(stored) : null
    if (parsed?.policy?.policy_number === policyRef) {
      data.value = parsed
      return
    }
    navigateTo(`/verifydetailspolicy?ref=${encodeURIComponent(policyRef)}`, { replace: true })
  } catch (e) {
    error.value = e.message || 'We could not open this policy.'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.docs-page { min-height: 100vh; background: #fff; font-family: var(--font); display: flex; flex-direction: column; color: #222; }
.bar { background: var(--brand-500); height: 52px; display: flex; align-items: center; padding: 0 1.5rem; }
.bar-logo { height: 22px; display: block; }

.wrap { width: 100%; max-width: 520px; margin: 0 auto; padding: 2rem 1.25rem 3rem; flex: 1; }

.h1 { font-size: 1.9rem; font-weight: 700; text-transform: uppercase; color: #3550A0; letter-spacing: 0.2px; margin-bottom: 0.9rem; }
.lede { color: #3550A0; font-size: 0.95rem; line-height: 1.5; margin-bottom: 2.25rem; }
.h2 { font-size: 1.75rem; font-weight: 700; text-transform: uppercase; color: #111; margin-bottom: 1.5rem; }

.details { border: 1px solid #BDBDBD; background: #F5F5F5; margin-bottom: 1.5rem; font-size: 0.95rem; }
.row { padding: 1rem 1.1rem; border-bottom: 1px solid #BDBDBD; line-height: 1.55; }
.row:last-child { border-bottom: none; }
.row.small { font-size: 0.82rem; color: #555; }
.lbl { font-weight: 700; margin-right: 0.25rem; }

.notice { padding: 0.85rem 1rem; border-radius: 6px; font-size: 0.9rem; margin-bottom: 1.5rem; }
.notice.info { background: #EEF3FF; color: #2A3F8F; border: 1px solid #C7D3F5; }
.notice.warn { background: #FFF4E5; color: #8A4B00; border: 1px solid #FFD8A8; }

.panel { border: 1px solid #4A8CF7; margin-bottom: 2rem; }
.panel-head { background: #4A8CF7; color: #fff; font-weight: 600; font-size: 1.1rem; padding: 0.95rem 1.1rem; }
.panel-body { background: #F7F9FC; padding: 1.1rem 1.1rem 1.25rem; }
.panel-note { font-size: 0.9rem; color: #444; line-height: 1.55; margin-bottom: 1.1rem; }
.panel-note a { color: #2F6FE0; }

.doc-list { list-style: none; display: flex; flex-direction: column; gap: 0.75rem; }
.doc-link { display: flex; align-items: center; gap: 0.75rem; color: #2F6FE0; text-decoration: underline; font-size: 1rem; }
.doc-link:hover { color: #1B4FB8; }
.pdf-icon { display: inline-flex; flex-shrink: 0; }

.btn-home { display: inline-block; background: #2E3F9E; color: #fff; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; padding: 0.9rem 1.5rem; border-radius: 2px; text-decoration: none; }
.btn-home:hover { background: #24327F; }

.loading { color: #666; padding: 2rem 0; }
.error-card { border: 1px solid #E5E7EB; border-radius: 8px; padding: 1.5rem; background: #FAFAFA; }
.error-text { color: #B42318; margin-bottom: 1.25rem; line-height: 1.5; }

.foot { text-align: center; font-size: 0.8rem; color: #777; padding: 1.25rem; border-top: 1px solid #EEE; }
.foot a { color: #777; text-decoration: none; }
.foot a:hover { color: var(--brand-600); }

@media (max-width: 480px) { .h1 { font-size: 1.5rem; } .h2 { font-size: 1.4rem; } .wrap { padding: 1.5rem 1rem 2.5rem; } }
</style>
