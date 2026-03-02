<template>
  <div class="px-6 py-4 pb-6 bg-bg-chat flex flex-col shrink-0 relative z-20">
    <PromptInputBox 
      v-model="text" 
      :hasFile="!!store.pendingFile" 
      :fileName="store.pendingFile?.name"
      :isRunning="store.processRunning"
      @send="send" 
      @upload="() => $refs.fileInput.click()" 
      @clearFile="clearFile"
      @stop="$emit('stop')"
      @togglePanel="store.panelVisible = !store.panelVisible"
      placeholder="Enter your request…"
    />
    <input
      ref="fileInput"
      type="file"
      accept=".pdf"
      class="hidden"
      @change="onFileSelected"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAppStore } from '@/stores/app'
import PromptInputBox from './PromptInputBox.vue'

const store = useAppStore()
const text = ref('')
const fileInput = ref(null)

const emit = defineEmits(['send', 'upload', 'stop'])

function send() {
  const trimmed = text.value.trim()
  if (!trimmed && !store.pendingFile) return

  if (store.pendingFile && !store.threadId) {
    emit('upload', trimmed)
  } else {
    emit('send', trimmed)
  }
  text.value = ''
}

function onFileSelected(e) {
  const file = e.target.files?.[0]
  if (file) store.pendingFile = file
}

function clearFile() {
  store.pendingFile = null
}
</script>
