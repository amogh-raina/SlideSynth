/**
 * Central Pinia store for all SlideSynth UI state.
 *
 * Replaces the scattered `let` variables in the old vanilla JS.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // ── Connection ──
  const threadId = ref(null)
  const connected = ref(false)
  const status = ref('Ready')
  const currentAgent = ref(null)
  const processStatus = ref('Waiting for project…')
  const processRunning = ref(false)

  // ── Chat messages ──
  // Each entry: { id, role: 'user'|'assistant', content, agent?, html? }
  const messages = ref([])
  let _nextId = 1

  function addMessage(role, content, agent = null, html = false) {
    const msg = { id: _nextId++, role, content, agent, html }
    messages.value.push(msg)
    return msg
  }

  // ── Thinking blocks ──
  // { id, agent, chunks: string, done: bool }
  const thinkingBlocks = ref([])
  let _activeThinking = null

  function appendThinking(agent, chunk) {
    if (!_activeThinking || _activeThinking.agent !== agent) {
      finaliseThinking()
      const block = { id: _nextId++, agent, chunks: chunk, done: false, startTime: Date.now(), endTime: null, duration: null }
      thinkingBlocks.value.push(block)
      messages.value.push({ id: block.id, type: 'thinking', blockId: block.id })
      _activeThinking = block
    } else {
      _activeThinking.chunks += chunk
    }
  }

  function finaliseThinking() {
    if (_activeThinking) {
      _activeThinking.done = true
      _activeThinking.endTime = Date.now()
      _activeThinking.duration = ((_activeThinking.endTime - _activeThinking.startTime) / 1000).toFixed(2)
      _activeThinking = null
    }
  }

  // ── Tool events ──
  function addToolEvent(evtType, agent, tool, value = '', logId = null, input = null) {
    messages.value.push({
      id: _nextId++,
      type: 'tool',
      evtType,
      agent,
      tool,
      value,
      logId,
      input,
      done: false,
    })
  }

  function completeToolEvent(toolName, output) {
    for (let i = messages.value.length - 1; i >= 0; i--) {
      const m = messages.value[i]
      if (m.type === 'tool' && m.tool === toolName && !m.done) {
        m.done = true
        m.value = output
        return
      }
    }
  }

  // ── Todos ──
  const todos = ref([])

  function updateTodos(newTodos) {
    todos.value = newTodos
    messages.value.push({
      id: _nextId++,
      type: 'todo',
      todos: [...newTodos],
    })
  }

  // ── Process terminal log ──
  // Each entry: { id, time, type, agent?, text, detail?, input?, output?, done? }
  const processLog = ref([])
  let _logId = 1

  function addProcessLog(type, text, agent = null, detail = null, input = null) {
    const id = _logId++
    processLog.value.push({
      id,
      time: new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      type,
      agent,
      text,
      detail,
      input,
      output: null,
      done: type !== 'tool_call',
    })
    return id
  }

  function completeToolLog(toolName, output) {
    // Find the last matching tool_call entry that isn't done yet
    for (let i = processLog.value.length - 1; i >= 0; i--) {
      const entry = processLog.value[i]
      if (entry.type === 'tool_call' && entry.text === toolName && !entry.done) {
        entry.output = output
        entry.done = true
        return
      }
    }
    // Fallback: add as standalone result
    addProcessLog('tool_result', toolName, null, output)
  }

  // ── Tool detail view ──
  const activeToolDetail = ref(null) // processLog entry or null

  function openToolDetail(entry) {
    activeToolDetail.value = entry
    activeTab.value = 'tool'
  }

  function closeToolDetail() {
    activeToolDetail.value = null
    activeTab.value = 'process'
  }

  // ── Interrupt ──
  const interrupt = ref(null) // { action, data } or null

  function showInterrupt(action, data = {}) {
    interrupt.value = { action, data }
  }
  function hideInterrupt() {
    interrupt.value = null
  }

  // ── File attachment ──
  const pendingFile = ref(null)

  // ── Projects / history ──
  const projects = ref([]) // [{ id, name, active }]

  function addProject(id, name) {
    projects.value.forEach(p => (p.active = false))
    projects.value.unshift({ id, name: name.replace('.pdf', ''), active: true })
  }
  function switchProject(id) {
    projects.value.forEach(p => (p.active = p.id === id))
  }

  // ── Right panel ──
  const activeTab = ref('process')
  const panelVisible = ref(false)
  const panelWidth = ref(468)

  // ── Open file tabs ──
  const openFiles = ref([])        // [{ path, name }]
  const activeFilePath = ref(null)

  function openFile(path) {
    if (!openFiles.value.find(f => f.path === path)) {
      const name = path.split('/').pop()
      openFiles.value.push({ path, name })
    }
    activeFilePath.value = path
    activeTab.value = 'files'
  }

  function closeFile(path) {
    const idx = openFiles.value.findIndex(f => f.path === path)
    if (idx === -1) return
    openFiles.value.splice(idx, 1)
    if (activeFilePath.value === path) {
      activeFilePath.value = openFiles.value.length
        ? openFiles.value[Math.max(0, idx - 1)].path
        : null
    }
  }

  function setActiveFile(path) {
    activeFilePath.value = path
  }

  // ── Files & slides ──
  const files = ref([])
  const slideCount = ref(0)
  const imageCount = computed(() =>
    files.value.filter(f => /\.(png|jpg|jpeg|gif|svg|webp)$/i.test(f)).length,
  )
  const tableCount = computed(() =>
    files.value.filter(f => f.startsWith('tables/') || f.startsWith('docs/tables/')).length,
  )

  // ── Presentation view ──
  const presView = ref('grid') // 'grid' | 'list'

  // ── Reset for new project ──
  function resetChat() {
    processLog.value = []
    _logId = 1
    activeToolDetail.value = null
    messages.value = []
    thinkingBlocks.value = []
    _activeThinking = null
    todos.value = []
    interrupt.value = null
    files.value = []
    openFiles.value = []
    activeFilePath.value = null
    slideCount.value = 0
    status.value = 'Ready'
    currentAgent.value = null
    processStatus.value = 'Waiting for project…'
    processRunning.value = false
  }

  // ── Restore messages from persisted chat history ──
  function loadChatHistory(events) {
    // events: [{ role: 'user'|'assistant', content: string }, ...]
    if (!events || !events.length) return
    for (const evt of events) {
      if (evt.role === 'user' || evt.role === 'assistant') {
        addMessage(evt.role, evt.content, evt.role === 'assistant' ? 'SlideSynth' : null)
      }
    }
  }

  return {
    // state
    threadId,
    connected,
    status,
    currentAgent,
    processStatus,
    processRunning,
    messages,
    thinkingBlocks,
    processLog,
    activeToolDetail,
    todos,
    interrupt,
    pendingFile,
    projects,
    activeTab,
    panelVisible,
    panelWidth,
    openFiles,
    activeFilePath,
    files,
    slideCount,
    imageCount,
    tableCount,
    presView,
    // actions
    addProcessLog,
    completeToolLog,
    openToolDetail,
    closeToolDetail,
    addMessage,
    appendThinking,
    finaliseThinking,
    addToolEvent,
    completeToolEvent,
    updateTodos,
    showInterrupt,
    hideInterrupt,
    addProject,
    switchProject,
    openFile,
    closeFile,
    setActiveFile,
    resetChat,
    loadChatHistory,
  }
})
