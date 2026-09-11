<template>
  <div class="page">
    <nav class="navbar">
      <div class="nav-inner">
        <NuxtLink to="/" class="nav-logo">
          <img src="/tempcover-logo-white.png" alt="TempCover" style="height:28px;" />
        </NuxtLink>
        <NuxtLink to="/admin/login" class="btn-login">Log In →</NuxtLink>
      </div>
    </nav>

    <div class="content-wrap">
      <h1>Terms & Conditions</h1>
      <p class="updated">Last updated: April 2026</p>

      <div class="section">
        <h2>1. Introduction</h2>
        <p>These Terms and Conditions govern your use of TempCover's short-term motor insurance platform. By using our services, you agree to be bound by these terms.</p>
      </div>

      <div class="section">
        <h2>2. Eligibility</h2>
        <p>To use our services, you must be at least 18 years of age, hold a valid UK driving licence, and have the vehicle owner's permission to drive the insured vehicle.</p>
      </div>

      <div class="section">
        <h2>3. Coverage</h2>
        <p>TempCover provides short-term motor insurance from 1 hour up to 28 days. Coverage options include Fully Comprehensive, Third Party Fire & Theft, and Third Party Only. Full details are outlined in your policy schedule.</p>
      </div>

      <div class="section">
        <h2>4. Policy Documents</h2>
        <p>All policy documents including your Certificate of Motor Insurance and Policy Schedule will be sent to the email address provided at the time of purchase. You are responsible for ensuring the email address is correct.</p>
      </div>

      <div class="section">
        <h2>5. Cancellation</h2>
        <p>Due to the short-term nature of our policies, cancellations and refunds are subject to our standard terms. Please contact us at <a href="mailto:support@tempcover-verify.com">support@tempcover-verify.com</a> for cancellation requests.</p>
      </div>

      <div class="section">
        <h2>6. Motor Insurance Database (MID)</h2>
        <p>Your insurance details will be submitted to the Motor Insurance Database within the required timeframe. Due to the temporary nature of the policy, there is a possibility the MID may not update before your policy expires. We recommend carrying your insurance certificate when driving.</p>
      </div>

      <div class="section">
        <h2>7. Liability</h2>
        <p>TempCover acts as an intermediary and is not the insurer. All claims are handled by the underwriting insurer as specified in your policy documents.</p>
      </div>

      <div class="section">
        <h2>8. Data Protection</h2>
        <p>We process your personal data in accordance with our Privacy Policy and applicable UK data protection law including the UK GDPR.</p>
      </div>

      <div class="section">
        <h2>9. Governing Law</h2>
        <p>These terms are governed by the laws of England and Wales. Any disputes shall be subject to the exclusive jurisdiction of the English courts.</p>
      </div>

      <div class="section">
        <h2>10. Contact</h2>
        <p>For any questions regarding these terms, please contact us at <a href="mailto:support@tempcover-verify.com">support@tempcover-verify.com</a>.</p>
      </div>
    </div>

    <footer>
      <div class="footer-inner">
        <img src="/tempcover-logo-white.png" alt="TempCover" style="height:22px;object-fit:contain;" />
        <div class="footer-links">
          <NuxtLink to="/terms">Terms & Conditions</NuxtLink>
          <NuxtLink to="/privacy">Privacy Policy</NuxtLink>
          <NuxtLink to="/contact">Contact Us</NuxtLink>
        </div>
        <span class="footer-copy">© 2026 TempCover. All rights reserved.</span>
      </div>
    </footer>
  </div>
</template>

<script setup>
useHead({ title: 'Terms & Conditions' })
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }
.page { font-family: Arial, Helvetica, sans-serif; background: #f8f8f8; min-height: 100vh; }

.navbar { background: var(--brand-500); position: sticky; top: 0; z-index: 100; }
.nav-inner { max-width: 1100px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; padding: 1rem 2rem; }
.nav-logo { display: flex; align-items: center; }
.btn-login { padding: 0.6rem 1.5rem; background: white; color: var(--brand-600); border-radius: 50px; font-size: 0.9rem; font-weight: 700; text-decoration: none; }
.btn-login:hover { background: var(--brand-50); }

.content-wrap { max-width: 760px; margin: 3rem auto; background: white; border-radius: 16px; padding: 3rem; box-shadow: 0 2px 16px rgba(0,0,0,0.06); }
h1 { font-size: 2rem; font-weight: 800; color: #1F2937; margin-bottom: 0.4rem; }
.updated { font-size: 0.85rem; color: #888; margin-bottom: 2rem; }
.section { margin-bottom: 2rem; }
.section h2 { font-size: 1.05rem; font-weight: 700; color: var(--brand-700); margin-bottom: 0.5rem; }
.section p { font-size: 0.92rem; color: #444; line-height: 1.7; }
.section a { color: var(--brand-600); text-decoration: none; }
.section a:hover { text-decoration: underline; }

footer { background: #1F2937; padding: 2rem; margin-top: 3rem; }
.footer-inner { max-width: 1100px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; }
.footer-links { display: flex; gap: 1.5rem; flex-wrap: wrap; }
.footer-links a { color: rgba(255,255,255,0.5); text-decoration: none; font-size: 0.8rem; }
.footer-links a:hover { color: white; }
.footer-copy { color: rgba(255,255,255,0.35); font-size: 0.78rem; }

@media (max-width: 768px) {
  .content-wrap { margin: 1.5rem 1rem; padding: 1.5rem; }
  .footer-inner { flex-direction: column; text-align: center; }
  .footer-links { justify-content: center; }
}
</style>