<template>
  <div>
    <div class="g-header">
      <div>
        <h1 class="g-title">Settings</h1>
        <p class="g-subtitle">Manage static documents shown to drivers</p>
      </div>
      <button class="g-btn g-btn-primary" @click="showForm = !showForm">+ Add Document</button>
    </div>

    <div v-if="toast.show" class="g-toast" :class="toast.type">{{ toast.message }}</div>

    <!-- Upload Form -->
    <div v-if="showForm" class="g-section" style="margin-bottom:1.5rem;">
      <div class="g-section-title">Add New Document</div>
      <div class="g-form-grid">
        <div class="g-field">
          <label>Document Name *</label>
          <input v-model="form.name" type="text" placeholder="e.g. Policy Wording" class="g-input" />
        </div>
        <div class="g-field">
          <label>Version</label>
          <input v-model="form.version" type="text" placeholder="v1.0" class="g-input" />
        </div>
      </div>

      <!-- Upload type toggle -->
      <div class="upload-toggle">
        <button :class="['toggle-btn', uploadType === 'file' ? 'active' : '']" @click="uploadType = 'file'">📁 Upload File</button>
        <button :class="['toggle-btn', uploadType === 'url' ? 'active' : '']" @click="uploadType = 'url'">🔗 URL Link</button>
      </div>

      <!-- File upload -->
      <div v-if="uploadType === 'file'" class="g-field" style="margin-top:1rem;">
        <label>PDF File *</label>
        <div class="file-drop" @click="$refs.fileInput.click()" @dragover.prevent @drop.prevent="onDrop">
          <input ref="fileInput" type="file" accept=".pdf" style="display:none" @change="onFileChange" />
          <div v-if="!selectedFile">
            <p class="file-drop-icon">📄</p>
            <p class="file-drop-text">Click or drag PDF file here</p>
          </div>
          <div v-else class="file-selected">
            <p>📄 {{ selectedFile.name }}</p>
            <p class="file-size">{{ (selectedFile.size / 1024).toFixed(1) }} KB</p>
          </div>
        </div>
      </div>

      <!-- URL input -->
      <div v-if="uploadType === 'url'" class="g-field" style="margin-top:1rem;">
        <label>Document URL *</label>
        <input v-model="form.url" type="url" placeholder="https://..." class="g-input" />
      </div>

      <div class="form-actions">
        <button class="g-btn g-btn-ghost" @click="cancelForm">Cancel</button>
        <button class="g-btn g-btn-primary" @click="addDocument" :disabled="saving">
          {{ saving ? 'Uploading...' : 'Save Document' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="g-loading">Loading...</div>

    <div v-else-if="docs.length === 0 && !showForm" class="g-empty">
      <div class="g-empty-icon">📄</div>
      <p class="g-empty-text">No static documents yet</p>
    </div>

    <div v-else class="docs-list">
      <div v-for="doc in docs" :key="doc.id" class="doc-row" :class="{ inactive: !doc.is_active }">
        <div class="doc-icon">📄</div>
        <div class="doc-info">
          <p class="doc-name">{{ doc.name }}
            <span v-if="doc.version" class="doc-ver">{{ doc.version }}</span>
          </p>
          <a :href="doc.url" target="_blank" class="doc-url">{{ doc.url }}</a>
        </div>
        <div class="doc-actions">
          <button class="g-btn g-btn-ghost doc-action-btn" @click="toggle(doc.id)">
            {{ doc.is_active ? 'Disable' : 'Enable' }}
          </button>
          <button class="g-btn g-btn-danger doc-action-btn" @click="remove(doc.id)">
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '~/stores/auth'
import { api } from '~/utils/api'

definePageMeta({ layout: 'superadmin' })
const auth = useAuthStore()
auth.init()

const docs = ref([])
const loading = ref(true)
const saving = ref(false)
const showForm = ref(false)
const uploadType = ref('file')
const selectedFile = ref(null)
const toast = ref({ show: false, message: '', type: 'success' })

const form = ref({ name: '', version: '', url: '' })

function showToast(msg, type = 'success') {
  toast.value = { show: true, message: msg, type }
  setTimeout(() => toast.value.show = false, 3000)
}

function onFileChange(e) {
  selectedFile.value = e.target.files[0] || null
}

function onDrop(e) {
  selectedFile.value = e.dataTransfer.files[0] || null
}

function cancelForm() {
  showForm.value = false
  selectedFile.value = null
  form.value = { name: '', version: '', url: '' }
}

async function addDocument() {
  if (!form.value.name) { showToast('Document name required', 'error'); return }

  saving.value = true
  try {
    if (uploadType.value === 'file') {
      if (!selectedFile.value) { showToast('Please select a file', 'error'); saving.value = false; return }

      const fd = new FormData()
      fd.append('name', form.value.name)
      fd.append('version', form.value.version)
      fd.append('file', selectedFile.value)

      const res = await fetch(api.url('/api/superadmin/settings/documents/upload'), {
        method: 'POST',
        headers: { Authorization: `Bearer ${auth.token}` },
        body: fd,
      })
      if (!res.ok) throw new Error('Upload failed')
      const doc = await res.json()
      docs.value.unshift(doc)
    } else {
      if (!form.value.url) { showToast('URL required', 'error'); saving.value = false; return }
      const doc = await api.post('/api/superadmin/settings/documents', {
        name: form.value.name, url: form.value.url, version: form.value.version
      }, auth.token)
      docs.value.unshift(doc)
    }

    showToast('Document added!')
    cancelForm()
  } catch(e) {
    showToast(e.message, 'error')
  } finally {
    saving.value = false
  }
}

async function toggle(id) {
  await api.patch(`/api/superadmin/settings/documents/${id}/toggle`, {}, auth.token)
  await load()
}

async function remove(id) {
  if (!confirm('Delete this document?')) return
  await api.delete(`/api/superadmin/settings/documents/${id}`, auth.token)
  docs.value = docs.value.filter(d => d.id !== id)
  showToast('Deleted')
}

async function load() {
  try { docs.value = await api.get('/api/superadmin/settings/documents', auth.token) }
  catch(e) { console.error(e) }
  finally { loading.value = false }
}

onMounted(load)
</script>

<style scoped>
/* ── Document list ── */
.docs-list { display: flex; flex-direction: column; gap: 0.75rem; }

.doc-row {
  background: white;
  border-radius: 12px;
  padding: 1rem 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: var(--card-shadow);
  border: 1px solid rgba(0,0,0,0.04);
  transition: all 0.18s;
}
.doc-row.inactive { opacity: 0.5; }

.doc-icon { font-size: 1.5rem; flex-shrink: 0; }

.doc-info { flex: 1; min-width: 0; }
.doc-name { font-weight: 700; color: var(--text-primary); font-size: 0.9rem; }
.doc-ver {
  font-size: 0.72rem; background: var(--brand-100);
  color: var(--brand-700); padding: 0.1rem 0.4rem;
  border-radius: 4px; margin-left: 0.5rem;
}
.doc-url {
  font-size: 0.72rem; color: var(--text-muted);
  white-space: nowrap; overflow: hidden;
  text-overflow: ellipsis; display: block;
  max-width: 100%;
}

.doc-actions { display: flex; gap: 0.5rem; flex-shrink: 0; }
.doc-action-btn { font-size: 0.78rem; padding: 0.3rem 0.75rem; }

/* ── Upload form ── */
.upload-toggle { display: flex; gap: 0.5rem; margin-top: 1rem; flex-wrap: wrap; }

.toggle-btn {
  flex: 1;
  padding: 0.5rem 1rem;
  border: 1.5px solid var(--gray-200);
  border-radius: 8px;
  background: white;
  color: var(--text-muted);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s;
  font-family: var(--font);
  white-space: nowrap;
  text-align: center;
}
.toggle-btn.active {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--brand-50);
}

.file-drop {
  border: 2px dashed var(--brand-300);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.18s;
  background: var(--brand-50);
}
.file-drop:hover { border-color: var(--accent); background: #FFEDE3; }
.file-drop-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.file-drop-text { font-size: 0.85rem; color: var(--text-muted); }
.file-selected p { font-weight: 600; color: var(--brand-700); }
.file-size { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem; }

/* Form action buttons row (Cancel / Save) */
.form-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

/* ── Inputs ── */
.g-input {
  padding: 0.72rem 0.875rem;
  border: 1.5px solid var(--gray-200);
  border-radius: 10px;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.18s;
  background: white;
  color: var(--text-primary);
  font-family: var(--font);
  width: 100%;
}
.g-input:focus { border-color: var(--brand-500); box-shadow: 0 0 0 3px rgba(255,81,0,0.1); }
.g-field label { font-size: 0.8rem; font-weight: 600; color: var(--brand-800); display: block; margin-bottom: 0.4rem; }

/* ── Responsive ── */
@media (max-width: 768px) {
  /* Keep "Add Document" header button from stretching full width */
  .g-header { align-items: stretch; }
  .g-header > button.g-btn { width: 100%; }

  /* Document row stacks vertically */
  .doc-row { flex-direction: column; align-items: flex-start; gap: 0.875rem; }

  /* Action buttons sit side-by-side and share the full row width */
  .doc-actions {
    width: 100%;
    display: flex;
    gap: 0.5rem;
  }
  /* Override global width:100% — each button takes half the row */
  .doc-actions .g-btn {
    flex: 1 1 0 !important;
    width: 0 !important;
    min-width: 0;
    justify-content: center;
    text-align: center;
    font-size: 0.82rem;
    padding: 0.5rem 0.5rem;
  }

  /* Upload toggle buttons already flex — just ensure they fill the row */
  .upload-toggle { flex-wrap: nowrap; }
  .toggle-btn { flex: 1 1 0; min-width: 0; }

  /* Form action buttons stack and go full width */
  .form-actions { flex-direction: column; }
  .form-actions .g-btn {
    width: 100% !important;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .doc-row { padding: 0.875rem 1rem; }
  .file-drop { padding: 1.5rem 1rem; }
  .g-form-grid { grid-template-columns: 1fr !important; }
}
</style>
