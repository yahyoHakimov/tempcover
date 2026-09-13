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
      <h1>Contact Us</h1>
      <p class="subtitle">We're here to help. Get in touch with our team.</p>

      <div class="cards">
        <div class="card">
          <div class="card-icon">✉️</div>
          <h3>Email Support</h3>
          <p>For policy enquiries, document requests, or general questions.</p>
          <a href="mailto:support@tempcovermyaccount.com">support@tempcovermyaccount.com</a>
        </div>
        <div class="card">
          <div class="card-icon">🕐</div>
          <h3>Response Time</h3>
          <p>We aim to respond to all enquiries within 24 hours on business days.</p>
          <span class="hours">Mon – Fri, 9am – 5pm GMT</span>
        </div>
        <div class="card">
          <div class="card-icon">📄</div>
          <h3>Document Issues</h3>
          <p>Can't access your policy documents? Contact us with your policy number.</p>
          <a href="mailto:support@tempcovermyaccount.com">Get Help</a>
        </div>
      </div>

      <div class="faq">
        <h2>Frequently Asked Questions</h2>

        <div class="faq-item">
          <h3>I haven't received my policy documents by email.</h3>
          <p>Please check your spam/junk folder. If still missing, contact us with your policy number and we will resend them.</p>
        </div>

        <div class="faq-item">
          <h3>How do I view my policy documents?</h3>
          <p>Click the "View your policy documents" button in the confirmation email you received. You'll need to verify your surname, date of birth, and policy start date.</p>
        </div>

        <div class="faq-item">
          <h3>Can I extend my policy?</h3>
          <p>Policy extensions are not available. Please contact your agent to create a new policy if you need additional cover.</p>
        </div>

        <div class="faq-item">
          <h3>Is my vehicle on the Motor Insurance Database (MID)?</h3>
          <p>Your details are submitted to the MID within the required timeframe. Due to the short-term nature of policies, the MID may not update before expiry. Carry your certificate as proof of insurance.</p>
        </div>
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
useHead({ title: 'Contact Us' })
</script>

<style scoped>
* { box-sizing: border-box; margin: 0; padding: 0; }
.page { font-family: Arial, Helvetica, sans-serif; background: #f8f8f8; min-height: 100vh; }
.navbar { background: var(--brand-500); position: sticky; top: 0; z-index: 100; }
.nav-inner { max-width: 1100px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; padding: 1rem 2rem; }
.nav-logo { display: flex; align-items: center; }
.btn-login { padding: 0.6rem 1.5rem; background: white; color: var(--brand-600); border-radius: 50px; font-size: 0.9rem; font-weight: 700; text-decoration: none; }
.btn-login:hover { background: var(--brand-50); }

.content-wrap { max-width: 860px; margin: 3rem auto; padding: 0 1rem; }
h1 { font-size: 2rem; font-weight: 800; color: #1F2937; margin-bottom: 0.4rem; }
.subtitle { color: #666; font-size: 1rem; margin-bottom: 2.5rem; }

.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.25rem; margin-bottom: 3rem; }
.card { background: white; border-radius: 16px; padding: 1.75rem; box-shadow: 0 2px 12px rgba(0,0,0,0.06); text-align: center; }
.card-icon { font-size: 2rem; margin-bottom: 0.75rem; display: block; }
.card h3 { font-size: 1rem; font-weight: 700; color: #1F2937; margin-bottom: 0.5rem; }
.card p { font-size: 0.85rem; color: #666; line-height: 1.6; margin-bottom: 0.75rem; }
.card a { color: var(--brand-600); font-weight: 600; font-size: 0.88rem; text-decoration: none; }
.card a:hover { text-decoration: underline; }
.hours { color: var(--brand-700); font-weight: 600; font-size: 0.85rem; }

.faq { background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 2px 12px rgba(0,0,0,0.06); margin-bottom: 3rem; }
.faq h2 { font-size: 1.2rem; font-weight: 800; color: #1F2937; margin-bottom: 1.5rem; }
.faq-item { border-bottom: 1px solid #f0f0f0; padding-bottom: 1.25rem; margin-bottom: 1.25rem; }
.faq-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.faq-item h3 { font-size: 0.92rem; font-weight: 700; color: var(--brand-700); margin-bottom: 0.4rem; }
.faq-item p { font-size: 0.88rem; color: #555; line-height: 1.6; }

footer { background: #1F2937; padding: 2rem; }
.footer-inner { max-width: 1100px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; }
.footer-links { display: flex; gap: 1.5rem; }
.footer-links a { color: rgba(255,255,255,0.5); text-decoration: none; font-size: 0.8rem; }
.footer-links a:hover { color: white; }
.footer-copy { color: rgba(255,255,255,0.35); font-size: 0.78rem; }

@media (max-width: 768px) {
  .cards { grid-template-columns: 1fr; }
  .footer-inner { flex-direction: column; text-align: center; }
  .footer-links { justify-content: center; }
}
</style>