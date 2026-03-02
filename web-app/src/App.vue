<template>
  <div class="flex h-full relative">
    <!-- Sidebar -->
    <AppSidebar
      :sidebar-width="sidebarWidth"
      :collapsed="sidebarCollapsed"
      @new-project="startNewProject"
      @switch-project="switchToProject"
      @toggle-collapse="sidebarCollapsed = !sidebarCollapsed"
    />
    <ResizeHandle
      v-if="!sidebarCollapsed"
      side="left"
      :get-width="() => sidebarWidth"
      @resize="w => sidebarWidth = w"
    />

    <!-- Center chat -->
    <ChatPanel
      @send="onSend"
      @upload="onUpload"
      @resume="onResume"
      @stop="onStop"
    />

    <!-- Right panel (floating overlay, animated) -->
    <Transition name="panel-slide">
      <RightPanel v-if="store.panelVisible" />
    </Transition>

    <!-- Hidden file input for new project -->
    <input
      ref="fileInput"
      type="file"
      accept=".pdf"
      class="hidden"
      @change="onGlobalFileSelected"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAppStore } from '@/stores/app'
import { useWebSocket } from '@/composables/useWebSocket'
import { useApi } from '@/composables/useApi'
import { uuid } from '@/lib/utils'
import AppSidebar from '@/components/AppSidebar.vue'
import ResizeHandle from '@/components/ResizeHandle.vue'
import ChatPanel from '@/components/ChatPanel.vue'
import RightPanel from '@/components/RightPanel.vue'

const store = useAppStore()
const ws = useWebSocket()
const api = useApi()

const sidebarWidth = ref(240)
const sidebarCollapsed = ref(false)
const fileInput = ref(null)

// Auto-open panel when PPT creation starts
watch(() => store.processRunning, (running) => {
  if (running) store.panelVisible = true
})

// Refresh files/slides whenever the WS signals
ws.onRefresh(() => {
  api.loadProjectFiles()
})

// ── Actions ──

function triggerFileInput() {
  fileInput.value?.click()
}

function onGlobalFileSelected(e) {
  const file = e.target.files?.[0]
  if (file) {
    store.pendingFile = file
  }
}

function ensureConnected() {
  if (!ws.isOpen) {
    if (!store.threadId) store.threadId = uuid()
    ws.connect(store.threadId)
  }
}

function startNewProject() {
  store.threadId = null
  store.resetChat()
  // Ensure we switch off active states in projects
  store.projects.forEach(p => p.active = false)
}

function onSend(text) {
  ensureConnected()
  // Small delay to let WS open
  if (!ws.isOpen) {
    setTimeout(() => {
      ws.sendChat(text)
    }, 500)
  } else {
    ws.sendChat(text)
  }
}

async function onUpload(text) {
  const file = store.pendingFile
  if (!file) return
  store.pendingFile = null
  store.status = 'Uploading…'

  try {
    const data = await api.uploadPdf(file)
    const tid = data.thread_id
    store.addProject(tid, file.name)
    ws.connect(tid)
    store.processStatus = 'Starting pipeline…'
    store.processRunning = true

    setTimeout(() => {
      if (ws.isOpen) {
        // Provide PDF path info conversationally — let the orchestrator
        // engage in chat mode instead of auto-commanding the pipeline.
        const pdfInfo = `The uploaded PDF '${file.name}' is at '${data.pdf_path}'.`
        const msg = text
          ? `${text}\n\n${pdfInfo}`
          : `I've uploaded a research paper: '${file.name}'. The PDF is at '${data.pdf_path}'.`
        ws.sendChat(msg)
      }
    }, 400)
  } catch (err) {
    store.status = 'Upload failed'
    alert(err.message)
  }
}

function onResume(decision, message) {
  ws.resume(decision, message)
}

function onStop() {
  ws.stopAgent()
}

async function switchToProject(id) {
  store.switchProject(id)
  store.resetChat()
  store.threadId = id
  ws.connect(id)
  await api.loadProjectFiles()
  // Restore persisted chat messages
  const history = await api.fetchChatHistory()
  store.loadChatHistory(history)
  if (store.slideCount > 0) {
    store.status = 'Done'
    store.processStatus = 'Completed'
  }
}

// Load existing projects on startup
onMounted(async () => {
  try {
    const projects = await api.listProjects()
    projects.slice(-10).forEach(id => {
      store.projects.push({ id, name: id.slice(0, 8) + '…', active: false })
    })
  } catch {
    // ignore
  }
})
</script>
