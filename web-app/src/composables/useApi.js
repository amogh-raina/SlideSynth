/**
 * REST API composable — wraps all /api/* calls.
 */
import { useAppStore } from '@/stores/app'

export function useApi() {
  const store = useAppStore()

  async function uploadPdf(file) {
    const form = new FormData()
    form.append('file', file)
    const resp = await fetch('/api/projects', { method: 'POST', body: form })
    const data = await resp.json()
    if (!resp.ok) throw new Error(data.detail || 'Upload failed')
    return data
  }

  async function listProjects() {
    const resp = await fetch('/api/projects')
    if (!resp.ok) return []
    const data = await resp.json()
    return data.projects || []
  }

  async function loadProjectFiles() {
    if (!store.threadId) return
    try {
      const resp = await fetch(`/api/projects/${store.threadId}`)
      if (!resp.ok) return
      const data = await resp.json()
      store.files = data.files || []
      store.slideCount = data.slide_count || 0
    } catch (e) {
      console.warn('loadProjectFiles error', e)
    }
  }

  function fileUrl(path) {
    return `/api/projects/${store.threadId}/files/${path}`
  }

  function presentationUrl() {
    return `/api/projects/${store.threadId}/presentation`
  }

  async function fetchFileText(path) {
    const resp = await fetch(fileUrl(path))
    return resp.text()
  }

  async function fetchChatHistory() {
    if (!store.threadId) return []
    try {
      const resp = await fetch(`/api/projects/${store.threadId}/chat`)
      if (!resp.ok) return []
      return await resp.json()
    } catch {
      return []
    }
  }

  return {
    uploadPdf,
    listProjects,
    loadProjectFiles,
    fileUrl,
    presentationUrl,
    fetchFileText,
    fetchChatHistory,
  }
}
