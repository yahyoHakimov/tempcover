<template>
  <div class="error-page">
    <div class="card">
      <img src="/tempcover-logo.png" alt="TempCover" class="logo" />
      <h1 class="code">{{ error?.statusCode || 500 }}</h1>
      <p class="message">
        {{ error?.statusCode === 404 ? 'This page could not be found.' : 'Something went wrong.' }}
      </p>
      <p class="detail" v-if="error?.statusCode === 404">
        The page you're looking for doesn't exist or may have moved.
      </p>
      <div class="actions">
        <a href="/verifydetailspolicy" class="btn-primary">My Insurance</a>
        <a href="/" class="btn-ghost">Home</a>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ error: Object })
</script>

<style scoped>
.error-page {
  min-height: 100vh;
  background: var(--main-bg, #F6F7F9);
  display: flex; align-items: center; justify-content: center;
  padding: 2rem 1rem;
  font-family: var(--font, 'Ubuntu', Arial, sans-serif);
}
.card {
  background: white; border-radius: 16px; padding: 3rem 2.5rem;
  max-width: 420px; width: 100%; text-align: center;
  border: 1px solid #E5E7EB; box-shadow: 0 12px 40px rgba(17,24,39,0.08);
}
.logo { height: 32px; margin-bottom: 1.5rem; }
.code { font-size: 3.5rem; font-weight: 700; color: #FF5100; line-height: 1; margin: 0 0 0.75rem; }
.message { font-size: 1.1rem; font-weight: 700; color: #1F2937; margin: 0 0 0.5rem; }
.detail { font-size: 0.875rem; color: #6B7280; line-height: 1.6; margin: 0 0 2rem; }
.actions { display: flex; gap: 0.75rem; justify-content: center; flex-wrap: wrap; }
.btn-primary {
  padding: 0.8rem 1.75rem; background: #FF5100; color: white; border-radius: 8px;
  font-size: 0.9rem; font-weight: 700; text-decoration: none; transition: background 0.2s;
}
.btn-primary:hover { background: #E64A00; }
.btn-ghost {
  padding: 0.8rem 1.5rem; border: 1.5px solid #E5E7EB; color: #374151; border-radius: 8px;
  font-size: 0.9rem; font-weight: 500; text-decoration: none; transition: all 0.2s;
}
.btn-ghost:hover { border-color: #FF5100; color: #FF5100; }
@media (max-width: 480px) { .card { padding: 2rem 1.5rem; } .actions { flex-direction: column; } }
</style>
