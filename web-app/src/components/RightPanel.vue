<template>
  <aside
    class="absolute top-14 right-3 bottom-3 z-40
           flex flex-col rounded-2xl overflow-hidden
           border border-border
           shadow-[0_12px_40px_rgba(0,0,0,0.12)]
           bg-[#ffffff] bg-[radial-gradient(#e5e5e5_1.5px,transparent_1.5px)] [background-size:16px_16px]"
    :style="{ width: store.panelWidth + 'px' }"
  >
    <!-- Resize handle (left edge) -->
    <div
      class="absolute top-0 left-0 bottom-0 w-1 cursor-col-resize z-50
             hover:bg-accent transition-colors"
      @mousedown.prevent="onResizeStart"
    />
    <!-- Header: tabs + close -->
    <div class="flex items-center px-3 py-2.5 shrink-0 gap-2">
      <!-- Pill tabs -->
      <div class="flex items-center gap-0.5 bg-bg-chat rounded-lg p-1">
        <button
          v-for="tab in visibleTabs"
          :key="tab.key"
          class="px-3.5 py-1.5 text-[13px] font-medium border-none cursor-pointer
                 rounded-md transition-all whitespace-nowrap"
          :class="store.activeTab === tab.key
            ? 'bg-white text-text shadow-sm'
            : 'bg-transparent text-text-muted hover:text-text'"
          @click="store.activeTab = tab.key"
        >
          {{ tab.label }}
        </button>

        <!-- Dynamic Tool tab -->
        <button
          v-if="store.activeToolDetail"
          class="flex items-center gap-1 px-3.5 py-1.5 text-[13px] font-medium border-none cursor-pointer
                 rounded-md transition-all whitespace-nowrap"
          :class="store.activeTab === 'tool'
            ? 'bg-white text-text shadow-sm'
            : 'bg-transparent text-text-muted hover:text-text'"
          @click="store.activeTab = 'tool'"
        >
          Tool
          <span
            class="text-[10px] leading-none cursor-pointer p-0.5 rounded hover:bg-bg-chat"
            @click.stop="store.closeToolDetail()"
          >&times;</span>
        </button>
      </div>

      <div class="flex-1" />

      <!-- Close button -->
      <button
        class="bg-transparent border-none text-text-muted cursor-pointer p-1 rounded-md
               hover:bg-bg-chat hover:text-text transition-colors"
        title="Close panel"
        @click="store.panelVisible = false"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- Tab content -->
    <div class="flex-1 overflow-hidden flex flex-col border-t border-border-light">
      <ProcessTab v-if="store.activeTab === 'process'" />
      <FilesTab v-else-if="store.activeTab === 'files'" :tree="fileTree" />
      <PresentationTab v-else-if="store.activeTab === 'presentation'" />
      <ToolDetailTab v-else-if="store.activeTab === 'tool'" />
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import ProcessTab from './ProcessTab.vue'
import FilesTab from './FilesTab.vue'
import PresentationTab from './PresentationTab.vue'
import ToolDetailTab from './ToolDetailTab.vue'

const store = useAppStore()

function onResizeStart(e) {
  const startX = e.clientX
  const startW = store.panelWidth
  document.body.classList.add('resizing')

  function onMove(ev) {
    const dx = startX - ev.clientX
    store.panelWidth = Math.max(320, Math.min(700, startW + dx))
  }
  function onUp() {
    document.body.classList.remove('resizing')
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
  }
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

const visibleTabs = computed(() => {
  const tabs = [
    { key: 'process', label: 'Current Process' },
    { key: 'files', label: 'Files' },
  ]
  if (store.slideCount > 0) {
    tabs.push({ key: 'presentation', label: 'Presentation' })
  }
  return tabs
})

/**
 * Build a nested tree structure from the flat file list.
 */
const fileTree = computed(() => {
  const files = store.files
  if (!files.length) return []

  const root = {}
  for (const f of files) {
    const parts = f.split('/')
    let node = root
    for (let i = 0; i < parts.length - 1; i++) {
      if (!node[parts[i]]) node[parts[i]] = { _children: {} }
      node = node[parts[i]]._children
    }
    node[parts[parts.length - 1]] = null
  }

  function toArray(obj, parentPath, depth) {
    const entries = Object.entries(obj).sort((a, b) => {
      const aDir = a[1] !== null ? 0 : 1
      const bDir = b[1] !== null ? 0 : 1
      return aDir - bDir || a[0].localeCompare(b[0])
    })

    return entries.map(([name, value]) => {
      const path = parentPath ? `${parentPath}/${name}` : name
      if (value !== null && value._children) {
        return {
          name,
          path,
          depth,
          children: toArray(value._children, path, depth + 1),
        }
      }
      return { name, path, depth }
    })
  }

  return toArray(root, '', 0)
})
</script>
