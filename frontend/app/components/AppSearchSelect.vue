<template>
  <div class="ss-wrap" ref="wrapRef">
    <!-- Trigger -->
    <button type="button" class="ss-trigger" :class="{ open: isOpen, selected: modelValue }" @click="toggle">
      <span class="ss-trigger-label">
        {{ modelValue ? getLabel(modelValue) : placeholder }}
      </span>
      <svg class="ss-chevron" :class="{ rotated: isOpen }" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline points="6 9 12 15 18 9"/>
      </svg>
    </button>

    <!-- Dropdown -->
    <div v-if="isOpen" class="ss-dropdown">
      <div class="ss-search-wrap">
        <svg class="ss-search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input
          ref="inputRef"
          v-model="query"
          type="text"
          class="ss-search"
          :placeholder="searchPlaceholder"
          @keydown.escape="close"
          @keydown.enter.prevent="selectFirst"
        />
      </div>

      <ul class="ss-list">
        <li
          v-for="option in filtered"
          :key="getKey(option)"
          class="ss-item"
          :class="{ active: modelValue && getKey(option) === getKey(modelValue) }"
          @click="select(option)"
        >
          <span class="ss-item-label">{{ getLabel(option) }}</span>
          <button
            v-if="removable"
            type="button"
            class="ss-remove"
            :title="`Delete ${getLabel(option)}`"
            @click.stop="emit('remove', option)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
              <line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>
            </svg>
          </button>
        </li>
        <li v-if="filtered.length === 0" class="ss-empty">No results found</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  options:          { type: Array,    required: true },
  getLabel:         { type: Function, required: true },  // (option) => string
  getKey:           { type: Function, default: (o) => o.id },
  placeholder:      { type: String,   default: 'Select...' },
  searchPlaceholder:{ type: String,   default: 'Type to search...' },
  removable:        { type: Boolean,  default: false },  // har bir qatorda delete tugmasi
  modelValue:       { default: null },
})

const emit = defineEmits(['update:modelValue', 'select', 'remove'])

const isOpen    = ref(false)
const query     = ref('')
const wrapRef   = ref(null)
const inputRef  = ref(null)

const filtered = computed(() => {
  const q = query.value.toLowerCase().trim()
  if (!q) return props.options
  return props.options.filter(o => props.getLabel(o).toLowerCase().includes(q))
})

function toggle() {
  if (isOpen.value) { close() } else { open() }
}

async function open() {
  isOpen.value = true
  query.value = ''
  await nextTick()
  inputRef.value?.focus()
}

function close() {
  isOpen.value = false
  query.value = ''
}

function select(option) {
  emit('update:modelValue', option)
  emit('select', option)
  close()
}

function selectFirst() {
  if (filtered.value.length > 0) select(filtered.value[0])
}

// Close on outside click
function onClickOutside(e) {
  if (wrapRef.value && !wrapRef.value.contains(e.target)) close()
}

onMounted(()  => document.addEventListener('mousedown', onClickOutside))
onUnmounted(() => document.removeEventListener('mousedown', onClickOutside))
</script>

<style scoped>
.ss-wrap { position: relative; width: 100%; }

/* Trigger button */
.ss-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.72rem 0.875rem;
  background: white;
  border: 1.5px solid var(--gray-200, #e5e7eb);
  border-radius: 10px;
  font-size: 0.875rem;
  font-family: var(--font, 'Inter', sans-serif);
  color: var(--text-muted, #9ca3af);
  cursor: pointer;
  transition: border-color 0.18s, box-shadow 0.18s;
  text-align: left;
}
.ss-trigger.selected { color: var(--text-primary, #1F2937); }
.ss-trigger.open,
.ss-trigger:hover  { border-color: var(--brand-500, #FF5100); }
.ss-trigger.open   { box-shadow: 0 0 0 3px rgba(255,81,0,0.1); }

.ss-trigger-label { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.ss-chevron {
  flex-shrink: 0;
  color: var(--text-muted, #9ca3af);
  transition: transform 0.2s;
}
.ss-chevron.rotated { transform: rotate(180deg); }

/* Dropdown */
.ss-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0; right: 0;
  background: white;
  border: 1.5px solid var(--brand-200, #FFD6C2);
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  z-index: 100;
  overflow: hidden;
}

/* Search input inside dropdown */
.ss-search-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.875rem;
  border-bottom: 1px solid var(--gray-100, #f3f4f6);
}
.ss-search-icon { flex-shrink: 0; color: var(--text-muted, #9ca3af); }
.ss-search {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.875rem;
  font-family: var(--font, 'Inter', sans-serif);
  color: var(--text-primary, #1F2937);
  background: transparent;
}

/* Options list */
.ss-list {
  list-style: none;
  max-height: 220px;
  overflow-y: auto;
  padding: 0.4rem 0;
}

.ss-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 0.875rem;
  font-size: 0.875rem;
  color: var(--text-primary, #1F2937);
  cursor: pointer;
  transition: background 0.12s;
}
.ss-item:hover  { background: var(--brand-50, #FFF7F2); }

.ss-item-label { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.ss-remove {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px; height: 26px;
  border: none;
  border-radius: 7px;
  background: transparent;
  color: var(--text-muted, #9ca3af);
  cursor: pointer;
  opacity: 0;
  transition: all 0.15s;
}
.ss-item:hover .ss-remove { opacity: 1; }
.ss-remove:hover { background: #fee2e2; color: #dc2626; }
@media (hover: none) { .ss-remove { opacity: 1; } }
.ss-item.active { background: var(--brand-100, #FFEDE3); color: var(--brand-700, #CC4100); font-weight: 600; }

.ss-empty {
  padding: 1rem 0.875rem;
  font-size: 0.82rem;
  color: var(--text-muted, #9ca3af);
  text-align: center;
}
</style>
