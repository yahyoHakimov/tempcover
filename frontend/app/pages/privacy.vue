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
      <h1>Privacy Policy</h1>
      <p class="updated">Last updated: April 2026</p>

      <div class="section">
        <h2>1. Who We Are</h2>
        <p>TempCover is a short-term motor insurance platform operated from the United Kingdom. For data protection purposes, we are the data controller of your personal information.</p>
      </div>

      <div class="section">
        <h2>2. Information We Collect</h2>
        <p>We collect the following personal data when you use our services: full name, date of birth, driving licence number, contact details (email, phone), address, vehicle information, and policy details.</p>
      </div>

      <div class="section">
        <h2>3. How We Use Your Information</h2>
        <p>Your personal data is used to issue and manage your insurance policy, send policy documents by email, verify your identity when accessing documents, and comply with legal and regulatory requirements including submission to the Motor Insurance Database (MID).</p>
      </div>

      <div class="section">
        <h2>4. Legal Basis</h2>
        <p>We process your data on the basis of contract performance (to provide the insurance service you requested), legal obligation (regulatory compliance), and legitimate interests (fraud prevention and service improvement).</p>
      </div>

      <div class="section">
        <h2>5. Data Sharing</h2>
        <p>We may share your data with the underwriting insurer, the Motor Insurance Database (MID), regulatory bodies as required by law, and our technology service providers who assist in operating this platform. We do not sell your personal data to third parties.</p>
      </div>

      <div class="section">
        <h2>6. Data Retention</h2>
        <p>We retain your personal data for a minimum of 7 years following the end of your policy in accordance with FCA requirements and applicable UK law.</p>
      </div>

      <div class="section">
        <h2>7. Your Rights</h2>
        <p>Under UK GDPR, you have the right to access, correct, or delete your personal data, object to processing, and request data portability. To exercise these rights, contact us at <a href="mailto:support@tempcover-verify.com">support@tempcover-verify.com</a>.</p>
      </div>

      <div class="section">
        <h2>8. Cookies</h2>
        <p>Our platform uses essential cookies only for authentication and session management. We do not use advertising or tracking cookies.</p>
      </div>

      <div class="section">
        <h2>9. Contact</h2>
        <p>For any privacy-related questions or to exercise your rights, please contact us at <a href="mailto:support@tempcover-verify.com">support@tempcover-verify.com</a>.</p>
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
useHead({ title: 'Privacy Policy' })
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
.footer-links { display: flex; gap: 1.5rem; }
.footer-links a { color: rgba(255,255,255,0.5); text-decoration: none; font-size: 0.8rem; }
.footer-links a:hover { color: white; }
.footer-copy { color: rgba(255,255,255,0.35); font-size: 0.78rem; }
@media (max-width: 768px) {
  .content-wrap { margin: 1.5rem 1rem; padding: 1.5rem; }
  .footer-inner { flex-direction: column; text-align: center; }
  .footer-links { justify-content: center; }
}
</style>