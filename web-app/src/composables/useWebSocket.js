/**
 * WebSocket composable — manages the real-time connection to the SlideSynth
 * backend.  Translates incoming JSON messages into Pinia store mutations.
 */
import { ref } from 'vue'
import { useAppStore } from '@/stores/app'

let _ws = null

export function useWebSocket() {
  const store = useAppStore()

  function connect(threadId) {
    store.threadId = threadId
    if (_ws) _ws.close()

    const proto = location.protocol === 'https:' ? 'wss' : 'ws'
    _ws = new WebSocket(`${proto}://${location.host}/ws/${threadId}`)

    _ws.onopen = () => {
      store.connected = true
      store.status = 'Connected'
    }
    _ws.onclose = () => {
      store.connected = false
      store.status = 'Disconnected'
    }
    _ws.onerror = () => {
      store.status = 'Connection error'
    }
    _ws.onmessage = (e) => handleMessage(JSON.parse(e.data))
  }

  function send(payload) {
    if (_ws && _ws.readyState === WebSocket.OPEN) {
      _ws.send(JSON.stringify(payload))
    }
  }

  function handleMessage(msg) {
    switch (msg.type) {
      case 'agent_start':
        store.currentAgent = msg.agent
        store.status = `Running: ${msg.agent}`
        store.processStatus = `${msg.agent} working…`
        store.processRunning = true
        store.addProcessLog('agent', `Agent started`, msg.agent)
        break

      case 'agent_done':
        store.finaliseThinking()
        store.addProcessLog('success', `Agent completed`, store.currentAgent)
        _emitRefresh()
        break

      case 'thinking':
        store.appendThinking(msg.agent, msg.content)
        break

      case 'tool_call': {
        const logId = store.addProcessLog('tool_call', msg.tool, msg.agent, null, msg.input || {})
        store.addToolEvent('tool_call', msg.agent, msg.tool, '', logId, msg.input || {})
        break
      }

      case 'tool_result':
        store.completeToolEvent(msg.tool, msg.output)
        store.completeToolLog(msg.tool, msg.output)
        if (/write_file|parse_pdf|generate_slide_html|combine_presentation|copy_asset/i.test(msg.tool)) {
          _emitRefresh()
        }
        break

      case 'todo_update':
        store.updateTodos(msg.todos)
        store.addProcessLog('info', `Task list updated (${msg.todos.length} items)`)
        break

      case 'interrupt':
        store.finaliseThinking()
        store.status = 'Awaiting approval'
        store.processStatus = 'Paused — awaiting approval'
        store.processRunning = false
        store.showInterrupt(msg.action, msg.data || {})
        store.addProcessLog('warn', `Interrupt: ${msg.action}`, store.currentAgent)
        break

      case 'error':
        store.finaliseThinking()
        store.addMessage('assistant', `❌ ${msg.message}`, 'SlideSynth')
        store.status = 'Error'
        store.processStatus = 'Error'
        store.processRunning = false
        store.addProcessLog('error', msg.message)
        break

      case 'complete':
        store.finaliseThinking()
        store.status = 'Done'
        store.processStatus = 'Completed'
        store.processRunning = false
        if (msg.message) store.addMessage('assistant', msg.message, 'SlideSynth')
        store.addProcessLog('success', 'Pipeline completed')
        _emitRefresh()
        break
    }
  }

  // Simple event bus for refresh signals (files/slides)
  const _refreshCallbacks = []
  function onRefresh(cb) {
    _refreshCallbacks.push(cb)
  }
  function _emitRefresh() {
    _refreshCallbacks.forEach(cb => cb())
  }

  function resume(decision, message = '') {
    send({ type: 'resume', decision, message })
    store.hideInterrupt()
    store.status = 'Resuming…'
    store.processStatus = 'Resuming…'
    store.processRunning = true
  }

  function sendChat(text) {
    store.addMessage('user', text)
    send({ type: 'chat', message: text })
  }

  function stopAgent() {
    send({ type: 'stop' })
    store.status = 'Stopping…'
    store.processStatus = 'Stopping…'
    store.processRunning = false
    store.addMessage('assistant', '⏹ Generation stopped.', 'SlideSynth')
  }

  return {
    connect,
    send,
    sendChat,
    resume,
    stopAgent,
    onRefresh,
    get isOpen() {
      return _ws && _ws.readyState === WebSocket.OPEN
    },
  }
}
