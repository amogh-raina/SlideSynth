<template>
  <div class="flex flex-col flex-1 min-h-0">
    <!-- Toolbar -->
    <div v-if="store.slideCount > 0" class="flex items-center gap-2 px-4 py-2.5 border-b border-border-light">
      <div class="flex border border-border rounded-md overflow-hidden">
        <button
          class="px-3 py-1 text-xs border-none cursor-pointer font-medium transition-colors"
          :class="store.presView === 'grid'
            ? 'bg-accent text-white'
            : 'bg-bg-card text-text-secondary hover:bg-bg-chat'"
          @click="store.presView = 'grid'"
        >Grid</button>
        <button
          class="px-3 py-1 text-xs border-none cursor-pointer font-medium transition-colors"
          :class="store.presView === 'list'
            ? 'bg-accent text-white'
            : 'bg-bg-card text-text-secondary hover:bg-bg-chat'"
          @click="store.presView = 'list'"
        >List</button>
      </div>
      <button
        class="ml-auto px-3.5 py-1.5 bg-text text-white border-none rounded-md text-xs font-medium
               flex items-center gap-1.5 hover:bg-gray-700 transition-colors cursor-pointer"
        @click="playPresentation"
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
          <polygon points="5,3 19,12 5,21" />
        </svg>
        Play Slides
      </button>
      <button
        v-if="store.slideCount > 0"
        class="ml-2 px-3.5 py-1.5 bg-accent text-white border-none rounded-md text-xs font-medium
               flex items-center gap-1.5 hover:bg-blue-700 transition-colors cursor-pointer"
        @click="requestExport"
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
        </svg>
        Export PDF
      </button>
    </div>

    <!-- Grid view -->
    <div
      v-if="store.slideCount > 0 && store.presView === 'grid'"
      class="grid grid-cols-2 gap-3 p-4 overflow-y-auto"
    >
      <div
        v-for="i in store.slideCount"
        :key="i"
        class="border border-border rounded-md overflow-hidden cursor-pointer
               transition-shadow hover:shadow-md"
        @click="openSlide(i)"
      >
        <div class="w-full aspect-[16/10] bg-bg-chat relative overflow-hidden">
          <iframe
            :src="slideUrl(i)"
            class="w-[400%] h-[400%] scale-25 origin-top-left border-none pointer-events-none"
            loading="lazy"
          />
        </div>
        <div class="px-2.5 py-1.5 flex items-center justify-between bg-bg-card">
          <span class="text-xs font-semibold text-text-secondary">{{ i }}</span>
          <div class="flex items-center gap-1.5">
            <span class="text-[11px] text-text-muted overflow-hidden text-ellipsis whitespace-nowrap max-w-[120px]">
              Slide {{ i }}
            </span>
            <button
              v-if="notes[i]"
              class="w-5 h-5 flex items-center justify-center text-[11px] rounded hover:bg-bg-chat
                     border-none bg-transparent cursor-pointer text-text-muted"
              :title="openNoteCard === i ? 'Hide notes' : 'Show notes'"
              @click.stop="toggleNote(i)"
            >📝</button>
          </div>
        </div>
        <!-- Collapsible speaker notes -->
        <div
          v-if="notes[i]"
          class="overflow-hidden transition-all duration-200 bg-bg-chat border-t border-border-light"
          :class="openNoteCard === i ? 'max-h-48 py-2 px-2.5' : 'max-h-0'"
        >
          <p class="text-[11px] leading-relaxed text-text-secondary m-0 overflow-y-auto max-h-40"
             v-html="escHtml(notes[i]).replace(/\n/g, '<br>')"></p>
        </div>
      </div>
    </div>

    <!-- List view -->
    <div
      v-if="store.slideCount > 0 && store.presView === 'list'"
      class="flex flex-col gap-2 p-4 overflow-y-auto"
    >
      <div
        v-for="i in store.slideCount"
        :key="i"
        class="flex gap-3 p-2.5 border border-border-light rounded-md cursor-pointer
               hover:bg-bg-chat transition-colors"
        @click="openSlide(i)"
      >
        <div class="w-40 shrink-0 aspect-[16/10] bg-bg-chat rounded overflow-hidden">
          <iframe
            :src="slideUrl(i)"
            class="w-[400%] h-[400%] scale-25 origin-top-left border-none pointer-events-none"
            loading="lazy"
          />
        </div>
        <div class="flex flex-col gap-0.5 min-w-0">
          <div class="text-[13px] font-semibold">Slide {{ i }}</div>
          <div class="text-xs text-text-muted leading-snug">{{ slideName(i) }}</div>
          <div
            v-if="notes[i]"
            class="mt-1 text-[11px] text-text-secondary leading-snug line-clamp-3"
          >{{ notes[i] }}</div>
        </div>
      </div>
    </div>

    <!-- Placeholder -->
    <div
      v-if="store.slideCount === 0"
      class="flex items-center justify-center flex-1 text-center text-text-muted px-10"
    >
      <div>
        <div class="text-5xl mb-3">📊</div>
        <p class="text-[13px]">Presentation will appear here<br>once slides are generated</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useAppStore } from '@/stores/app'
import { useApi } from '@/composables/useApi'
import { useWebSocket } from '@/composables/useWebSocket'

const store = useAppStore()
const api = useApi()
const ws = useWebSocket()

function requestExport() {
  ws.sendChat("Please export the presentation to PDF.")
}

/* ── Speaker notes ─────────────────────────────── */
const notes = ref({})           // { 1: "…", 2: "…" }
const openNoteCard = ref(null)  // which grid card is expanded

async function loadNotes() {
  try {
    const resp = await fetch(api.fileUrl('slides/speaker_notes.json'))
    if (!resp.ok) { notes.value = {}; return }
    const arr = await resp.json()
    const map = {}
    arr.forEach(e => { map[e.slide] = e.notes })
    notes.value = map
  } catch { notes.value = {} }
}

// Reload notes whenever slide count changes (new generation)
watch(() => store.slideCount, (n) => { if (n > 0) loadNotes() }, { immediate: true })

function toggleNote(i) {
  openNoteCard.value = openNoteCard.value === i ? null : i
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
}

/* ── Helpers ───────────────────────────────────── */
function slideUrl(i) {
  const n = String(i).padStart(2, '0')
  return api.fileUrl(`slides/slide${n}.html`)
}

function slideName(i) {
  const n = String(i).padStart(2, '0')
  return `slide${n}.html`
}

function openSlide(i) {
  window.open(slideUrl(i), '_blank')
}

function playPresentation() {
  window.open(api.presentationUrl(), '_blank')
}
</script>
