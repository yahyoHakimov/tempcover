<template>
  <div class="portal-page">
    <header class="header">
      <img src="/tempcover-logo-white.png" alt="TempCover" class="header-logo" />
      <div class="header-right" v-if="data">
        <span class="welcome">Hi, {{ data.driver.first_name }}</span>
        <button class="logout-btn" @click="logout">Sign out</button>
      </div>
    </header>

    <div class="container" v-if="data">

      <!-- Hero -->
      <div class="policy-hero">
        <div class="hero-top">
          <span class="policy-badge" :class="isExpired ? 'badge-expired' : 'badge-active'">{{ data.policy.status }}</span>
          <span class="hero-num">Policy {{ data.policy.policy_number }}</span>
        </div>
        <h1 class="hero-welcome">Welcome, {{ data.driver.first_name }}</h1>
        <p class="policy-cover">{{ coverLabel(data.policy.cover_type) }} · {{ data.vehicle.registration }}</p>
      </div>

      <div class="status-banner" v-if="isExpired">
        This policy has expired or has been cancelled. Documents are no longer available.
      </div>

      <!-- Policy -->
      <div class="section-card">
        <div class="section-title">Policy details</div>
        <div class="info-row"><span class="info-label">Policy number</span><span class="info-value">{{ data.policy.policy_number }}</span></div>
        <div class="info-row"><span class="info-label">Cover</span><span class="info-value">{{ coverLabel(data.policy.cover_type) }}</span></div>
        <div class="info-row"><span class="info-label">Policy start</span><span class="info-value">{{ data.policy.start_datetime }}</span></div>
        <div class="info-row"><span class="info-label">Policy end</span><span class="info-value">{{ data.policy.end_datetime }}</span></div>
        <div class="info-row"><span class="info-label">Policyholder</span><span class="info-value">{{ data.driver.first_name }} {{ data.driver.last_name }} (main driver)</span></div>
        <div class="info-row"><span class="info-label">Premium paid</span><span class="info-value">£{{ Number(data.policy.price).toFixed(2) }}</span></div>
        <div class="info-row"><span class="info-label">Countries covered</span><span class="info-value">United Kingdom</span></div>
      </div>

      <!-- Vehicle -->
      <div class="section-card">
        <div class="section-title">Vehicle</div>
        <div class="info-row"><span class="info-label">Registration</span><span class="reg">{{ data.vehicle.registration }}</span></div>
        <div class="info-row"><span class="info-label">Make &amp; model</span><span class="info-value">{{ data.vehicle.make }} {{ data.vehicle.model }}</span></div>
        <div class="info-row" v-if="data.vehicle.colour"><span class="info-label">Colour</span><span class="info-value">{{ data.vehicle.colour }}</span></div>
      </div>

      <!-- Documents -->
      <div class="section-card" v-if="!isExpired">
        <div class="section-title">Your documents</div>
        <p class="docs-note">Open or download your policy documents. Keep your certificate with you when driving.</p>

        <a v-for="doc in data.dynamic_docs" :key="doc.name" :href="doc.url" target="_blank" rel="noopener" class="doc-item">
          <span class="doc-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          </span>
          <span class="doc-name">{{ doc.name }}</span>
          <span class="doc-open">Open</span>
        </a>

        <template v-if="data.static_docs && data.static_docs.length">
          <div class="docs-divider">Policy wording &amp; information</div>
          <a v-for="doc in data.static_docs" :key="doc.name" :href="doc.url" target="_blank" rel="noopener" class="doc-item">
            <span class="doc-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            </span>
            <span class="doc-name">{{ doc.name }}</span>
            <span class="doc-open">Open</span>
          </a>
        </template>
      </div>
      <div class="section-card" v-else>
        <div class="section-title">Your documents</div>
        <p class="docs-note">Documents are not available for expired or cancelled policies.</p>
      </div>

      <!-- Help -->
      <div class="section-card">
        <div class="section-title">Need help?</div>
        <p class="help-text">Our team is here for you. Email <a :href="`mailto:${supportEmail}`" class="help-link">{{ supportEmail }}</a> and we'll get back to you within one working day.</p>
      </div>
    </div>

    <div v-else class="no-data">
      <p>Your session has ended. <NuxtLink to="/driver/login">Sign in again</NuxtLink></p>
    </div>

    <footer class="site-footer">
      <div class="footer-inner">
        <img src="/tempcover-logo-white.png" alt="TempCover" class="footer-logo" />
        <p class="footer-legal">
          TempCover is an insurance intermediary authorised and regulated by the Financial Conduct Authority.
          TempCover Ltd is registered in England and Wales.
        </p>
        <div class="footer-links">
          <NuxtLink to="/privacy">Privacy policy</NuxtLink>
          <span class="footer-sep">·</span>
          <NuxtLink to="/terms">Terms &amp; conditions</NuxtLink>
          <span class="footer-sep">·</span>
          <NuxtLink to="/contact">Contact us</NuxtLink>
        </div>
        <div class="footer-secure">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          <div>
            <p class="secure-title">Your details are secure</p>
            <p class="secure-sub">We use industry-standard encryption to keep your information safe.</p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '~/utils/api'

definePageMeta({ layout: false })
useHead({ title: 'My Insurance' })

const supportEmail = 'support@tempcover-verify.com'
const data = ref(null)

const COVER = { fully_comprehensive: 'Fully Comprehensive', third_party_fire_theft: 'Third Party, Fire & Theft', third_party_only: 'Third Party Only' }
const coverLabel = (c) => COVER[c] || 'Fully Comprehensive'

const isExpired = computed(() => {
  const s = data.value?.policy?.status?.toLowerCase()
  return s === 'expired' || s === 'cancelled'
})

onMounted(async () => {
  const stored = localStorage.getItem('driver_portal_data')
  if (!stored) { navigateTo('/driver/login', { replace: true }); return }
  try { data.value = JSON.parse(stored) }
  catch { navigateTo('/driver/login', { replace: true }); return }

  // Refresh the static documents so newly published wording shows without re-login
  try {
    const fresh = await api.get('/api/drivers/portal/documents')
    if (Array.isArray(fresh)) data.value = { ...data.value, static_docs: fresh }
  } catch { /* non-critical */ }
})

function logout() {
  localStorage.removeItem('driver_portal_data')
  navigateTo('/driver/login', { replace: true })
}
</script>

<style scoped>
.portal-page { min-height: 100vh; background: var(--main-bg); font-family: var(--font); display: flex; flex-direction: column; }

.header { background: var(--brand-500); height: var(--topbar-h); padding: 0 1.5rem; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 2px 8px rgba(255,81,0,0.25); }
.header-logo { height: 26px; }
.header-right { display: flex; align-items: center; gap: 1rem; }
.welcome { color: rgba(255,255,255,0.9); font-size: 0.875rem; font-weight: 500; }
.logout-btn { background: rgba(255,255,255,0.14); border: 1px solid rgba(255,255,255,0.35); color: white; padding: 0.42rem 0.8rem; border-radius: 8px; font-size: 0.82rem; font-weight: 500; cursor: pointer; transition: all 0.15s; font-family: inherit; }
.logout-btn:hover { background: white; color: var(--brand-600); }

.container { max-width: 640px; width: 100%; margin: 0 auto; padding: 1.5rem 1rem 2.5rem; display: flex; flex-direction: column; gap: 1rem; flex: 1; }

.policy-hero { background: linear-gradient(135deg, var(--brand-600), var(--brand-400)); border-radius: 14px; padding: 1.75rem; color: white; box-shadow: 0 8px 24px rgba(255,81,0,0.25); }
.hero-top { display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; margin-bottom: 0.9rem; }
.hero-num { font-size: 0.8rem; opacity: 0.85; font-weight: 500; }
.policy-badge { display: inline-flex; padding: 0.25rem 0.75rem; border-radius: 50px; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.badge-active { background: rgba(255,255,255,0.22); color: white; }
.badge-expired { background: white; color: var(--error); }
.hero-welcome { font-size: 1.5rem; font-weight: 700; margin-bottom: 0.3rem; }
.policy-cover { font-size: 0.875rem; opacity: 0.9; }

.status-banner { background: var(--error-bg); border: 1.5px solid var(--error-border); color: var(--error); border-radius: 10px; padding: 0.875rem 1.25rem; font-size: 0.875rem; font-weight: 500; text-align: center; }

.section-card { background: white; border-radius: 14px; padding: 1.5rem; border: 1px solid var(--card-border); box-shadow: var(--card-shadow); }
.section-title { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: var(--brand-600); margin-bottom: 1rem; }

.info-row { display: flex; justify-content: space-between; align-items: flex-start; padding: 0.6rem 0; border-bottom: 1px solid var(--gray-100); font-size: 0.875rem; gap: 1rem; }
.info-row:last-child { border-bottom: none; }
.info-label { color: var(--text-muted); flex-shrink: 0; }
.info-value { font-weight: 500; color: var(--text-primary); text-align: right; }
.reg { font-family: 'Courier New', monospace; font-weight: 700; background: #FFE600; color: #111; padding: 0.15rem 0.55rem; border-radius: 4px; letter-spacing: 1px; border: 1px solid #E5CF00; }

.docs-note { font-size: 0.82rem; color: var(--text-muted); margin-bottom: 1rem; line-height: 1.5; }
.doc-item { display: flex; align-items: center; gap: 0.875rem; padding: 0.875rem; border: 1.5px solid var(--gray-200); border-radius: 10px; text-decoration: none; color: var(--text-primary); transition: all 0.15s; margin-bottom: 0.5rem; }
.doc-item:last-child { margin-bottom: 0; }
.doc-item:hover { border-color: var(--brand-400); background: var(--brand-50); }
.doc-icon { color: var(--brand-500); display: flex; flex-shrink: 0; }
.doc-name { flex: 1; font-size: 0.875rem; font-weight: 500; }
.doc-open { font-size: 0.78rem; color: var(--brand-600); font-weight: 600; flex-shrink: 0; }
.docs-divider { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); margin: 0.9rem 0 0.5rem; }

.help-text { font-size: 0.875rem; color: var(--text-secondary); line-height: 1.6; }
.help-link { color: var(--brand-600); font-weight: 600; text-decoration: none; }
.help-link:hover { text-decoration: underline; }

.no-data { text-align: center; padding: 3rem; color: var(--text-muted); flex: 1; }
.no-data a { color: var(--brand-600); font-weight: 600; }

.site-footer { background: var(--gray-800); color: rgba(255,255,255,0.6); margin-top: auto; padding: 2rem 1.5rem; }
.footer-inner { max-width: 700px; margin: 0 auto; display: flex; flex-direction: column; gap: 1rem; }
.footer-logo { height: 22px; align-self: flex-start; }
.footer-legal { font-size: 0.78rem; line-height: 1.6; color: rgba(255,255,255,0.55); }
.footer-links { display: flex; flex-wrap: wrap; gap: 0.4rem 0.6rem; font-size: 0.8rem; align-items: center; }
.footer-links a { color: rgba(255,255,255,0.8); text-decoration: none; }
.footer-links a:hover { color: white; }
.footer-sep { color: rgba(255,255,255,0.25); }
.footer-secure { display: flex; align-items: flex-start; gap: 0.75rem; margin-top: 0.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); }
.footer-secure svg { flex-shrink: 0; margin-top: 2px; color: var(--brand-300); }
.secure-title { font-size: 0.82rem; font-weight: 700; color: rgba(255,255,255,0.85); margin-bottom: 0.2rem; }
.secure-sub { font-size: 0.75rem; line-height: 1.5; color: rgba(255,255,255,0.45); }

@media (max-width: 480px) {
  .header { padding: 0 1rem; }
  .welcome { display: none; }
  .policy-hero { padding: 1.25rem; }
  .hero-welcome { font-size: 1.2rem; }
  .section-card { padding: 1.25rem 1rem; }
  .info-row { flex-direction: column; align-items: flex-start; gap: 0.2rem; }
  .info-value { text-align: left; }
  .footer-links { flex-direction: column; gap: 0.4rem; }
  .footer-sep { display: none; }
}
</style>
