<template>
  <div class="flex flex-1 min-h-0">
    <!-- Left: file tree -->
    <div class="w-[220px] shrink-0 border-r border-border-light flex flex-col min-h-0">
      <!-- Tree header -->
      <div class="flex items-center justify-between px-4 py-3 shrink-0">
        <span class="text-[14px] font-semibold text-text">Files</span>
        <button
          class="bg-transparent border-none text-text-muted cursor-pointer p-1 rounded-md
                 hover:bg-bg-chat hover:text-text transition-colors"
          title="Refresh files"
          @click="$emit('refresh')"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 2v6h-6M3 12a9 9 0 0115.36-6.36L21 8M3 22v-6h6M21 12a9 9 0 01-15.36 6.36L3 16"/>
          </svg>
        </button>
      </div>

      <!-- Search -->
      <div class="px-3 pb-2 shrink-0">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search Files..."
          class="w-full px-3 py-2 text-[13px] border border-border rounded-lg bg-bg-chat
                 outline-none placeholder-text-muted transition-colors focus:border-text-muted"
        />
      </div>

      <!-- Tree -->
      <div class="flex-1 overflow-y-auto px-2 pb-2 text-[13.5px]">
        <div v-if="!filteredTree.length" class="py-5 text-center text-text-muted text-[13px]">
          No project files yet
        </div>
        <template v-for="node in filteredTree" :key="node.path">
          <FileNode
            :node="node"
            :active-path="store.activeFilePath"
            @preview="onFileClick"
          />
        </template>
      </div>
    </div>

    <!-- Right: file preview area -->
    <div class="flex-1 flex flex-col min-h-0 min-w-0">
      <!-- Open file tabs -->
      <div v-if="store.openFiles.length" class="flex items-center border-b border-border-light bg-bg-card shrink-0 overflow-x-auto">
        <div
          v-for="file in store.openFiles"
          :key="file.path"
          class="flex items-center gap-1.5 px-3.5 py-2 text-[13px] cursor-pointer border-r border-border-light
                 whitespace-nowrap transition-colors shrink-0 group"
          :class="store.activeFilePath === file.path
            ? 'bg-white text-text font-medium'
            : 'bg-bg-card text-text-muted hover:text-text hover:bg-bg-chat'"
          @click="store.setActiveFile(file.path)"
        >
          <span class="text-[11px]">{{ fileTabIcon(file.name) }}</span>
          {{ file.name }}
          <button
            class="bg-transparent border-none text-text-muted cursor-pointer p-0 ml-1 rounded-sm
                   opacity-0 group-hover:opacity-100 hover:text-red transition-all text-[11px] leading-none"
            @click.stop="store.closeFile(file.path)"
          >×</button>
        </div>
      </div>

      <!-- Active file preview -->
      <template v-if="activeFile">
        <!-- Breadcrumb + actions bar -->
        <div class="flex items-center gap-2 px-4 py-2 border-b border-border-light shrink-0 bg-bg-card">
          <span class="text-[12.5px] text-text-secondary overflow-hidden text-ellipsis whitespace-nowrap flex-1">
            {{ activeFile.path }}
          </span>

          <!-- Preview / Code toggle for HTML -->
          <div v-if="activeExt === 'html'" class="flex bg-bg-chat rounded-lg overflow-hidden border border-border shrink-0">
            <button
              class="px-3.5 py-1 text-[12.5px] font-medium border-none cursor-pointer transition-colors"
              :class="viewMode === 'preview'
                ? 'bg-white text-text shadow-sm'
                : 'bg-transparent text-text-muted hover:text-text'"
              @click="viewMode = 'preview'"
            >Preview</button>
            <button
              class="px-3.5 py-1 text-[12.5px] font-medium border-none cursor-pointer transition-colors"
              :class="viewMode === 'code'
                ? 'bg-white text-text shadow-sm'
                : 'bg-transparent text-text-muted hover:text-text'"
              @click="switchToCode"
            >Code</button>
          </div>

          <!-- Download button -->
          <a
            :href="api.fileUrl(activeFile.path)"
            :download="activeFile.name"
            class="bg-transparent border-none text-text-muted cursor-pointer p-1 rounded-md
                   hover:bg-bg-chat hover:text-text transition-colors inline-flex"
            title="Download"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
            </svg>
          </a>
        </div>

        <!-- Content area -->
        <div class="flex-1 overflow-auto relative">
          <!-- Image -->
          <img
            v-if="isActiveImage"
            :src="api.fileUrl(activeFile.path)"
            class="max-w-full h-auto rounded-md block mx-auto p-4"
          />
          <!-- HTML preview -->
          <iframe
            v-else-if="activeExt === 'html' && viewMode === 'preview'"
            :src="api.fileUrl(activeFile.path)"
            class="w-full h-full border-none"
          />
          <!-- HTML code -->
          <pre
            v-else-if="activeExt === 'html' && viewMode === 'code'"
            class="text-[12.5px] leading-relaxed whitespace-pre-wrap break-words bg-bg-chat m-0 p-4"
          >{{ previewContent }}</pre>
          <!-- PDF -->
          <iframe
            v-else-if="activeExt === 'pdf'"
            :src="api.fileUrl(activeFile.path)"
            class="w-full h-full border-none"
          />
          <!-- Markdown -->
          <div
            v-else-if="activeExt === 'md'"
            class="prose-file text-[14px] leading-relaxed text-text p-4"
            v-html="previewContent"
          />
          <!-- JSON / text -->
          <pre
            v-else
            class="text-[12.5px] leading-relaxed whitespace-pre-wrap break-words bg-bg-chat m-0 p-4"
          >{{ previewContent }}</pre>
        </div>
      </template>

      <!-- Empty state -->
      <div v-else class="flex-1 flex items-center justify-center">
        <span class="text-[15px] text-text-muted">Select a file to view</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useAppStore } from '@/stores/app'
import { useApi } from '@/composables/useApi'
import { marked } from 'marked'
import { fileIcon } from '@/lib/utils'
import FileNode from './FileNode.vue'

const props = defineProps({
  tree: { type: Array, default: () => [] },
})

defineEmits(['refresh'])

const store = useAppStore()
const api = useApi()

const searchQuery = ref('')
const viewMode = ref('preview')
const previewContent = ref('')

// Active file helpers
const activeFile = computed(() =>
  store.openFiles.find(f => f.path === store.activeFilePath) || null,
)

const activeExt = computed(() => {
  if (!activeFile.value) return ''
  return activeFile.value.name.split('.').pop().toLowerCase()
})

const isActiveImage = computed(() =>
  /^(png|jpg|jpeg|gif|svg|webp)$/.test(activeExt.value),
)

function fileTabIcon(name) {
  return fileIcon(name)
}

// Filter tree by search
const filteredTree = computed(() => {
  const tree = props.tree || []
  if (!searchQuery.value.trim()) return tree
  const q = searchQuery.value.toLowerCase()
  return filterNodes(tree, q)
})

function filterNodes(nodes, query) {
  return nodes
    .map(node => {
      if (node.children) {
        const filtered = filterNodes(node.children, query)
        if (filtered.length || node.name.toLowerCase().includes(query)) {
          return { ...node, children: filtered }
        }
        return null
      }
      return node.name.toLowerCase().includes(query) ? node : null
    })
    .filter(Boolean)
}

// Load content when active file changes
watch(
  () => store.activeFilePath,
  async (path) => {
    if (!path) return
    viewMode.value = 'preview'
    previewContent.value = ''

    const ext = path.split('.').pop().toLowerCase()
    if (/^(png|jpg|jpeg|gif|svg|webp|html|pdf)$/.test(ext)) return

    try {
      const text = await api.fetchFileText(path)
      if (ext === 'json') {
        try {
          previewContent.value = JSON.stringify(JSON.parse(text), null, 2)
        } catch {
          previewContent.value = text
        }
      } else if (ext === 'md') {
        previewContent.value = marked.parse(text, { breaks: true })
      } else {
        previewContent.value = text
      }
    } catch {
      previewContent.value = 'Failed to load file'
    }
  },
)

function onFileClick(path) {
  store.openFile(path)
}

async function switchToCode() {
  viewMode.value = 'code'
  if (!previewContent.value && activeFile.value) {
    try {
      previewContent.value = await api.fetchFileText(activeFile.value.path)
    } catch {
      previewContent.value = 'Failed to load source'
    }
  }
}
</script>
