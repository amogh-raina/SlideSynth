<template>
  <section class="flex-1 flex flex-col min-w-0 bg-bg-chat relative transition-all duration-350 ease-[cubic-bezier(0.16,1,0.3,1)]"
           :style="{ marginRight: store.panelVisible ? (store.panelWidth + 16) + 'px' : '0px' }">
    <!-- Header (stays fixed, never moves) -->
    <div class="px-6 py-3.5 border-b border-border bg-bg-sidebar flex items-center gap-3 shrink-0 z-10">
      <img :src="logoUrl" class="w-6 h-6" alt="" />
      <div class="text-[15px] font-semibold text-text">SlideSynth</div>
      <span
        v-if="store.currentAgent"
        class="text-[11.5px] px-2.5 py-0.5 rounded-full font-medium text-white"
        :style="{ background: getAgentColor(store.currentAgent) }"
      >
        {{ store.currentAgent }}
      </span>
      <span class="ml-auto text-[13px] text-text-muted">{{ store.status }}</span>
    </div>

    <!-- Landing page (shown when no conversation) -->
    <div
      v-if="store.messages.length === 0"
      class="flex-1 flex flex-col items-center justify-center px-8 pb-32"
    >
      <div class="max-w-3xl w-full text-center">
        <!-- Tagline with word animation -->
        <h1 class="text-[44px] font-semibold text-text mb-12 leading-tight tracking-tight">
          <TypewriterText
            :text="['Welcome to SlideSynth', 'Build an awesome presentation']"
            :speed="70"
            :delay="2500"
            :loop="true"
            className="text-[44px] font-semibold"
          />
        </h1>

        <!-- Inline input area (landing) -->
        <PromptInputBox 
          v-model="landingText" 
          :hasFile="!!store.pendingFile" 
          :fileName="store.pendingFile?.name"
          @send="onLandingSend" 
          @upload="() => $refs.landingFileInput.click()" 
          @clearFile="store.pendingFile = null"
          @togglePanel="() => store.panelVisible = !store.panelVisible"
          placeholder="Enter your task and submit it to SlideSynth Agent."
        />
        <input
          ref="landingFileInput"
          type="file"
          accept=".pdf"
          class="hidden"
          @change="onLandingFileSelected"
        />
      </div>
    </div>

    <!-- Messages (shown when conversation is active) -->
    <div
      v-else ref="messagesEl"
      class="flex-1 overflow-y-auto px-6 py-6 flex flex-col gap-4"
    >
      <template v-for="group in groupedMessages" :key="group.id">
        <!-- Regular message -->
        <ChatMessage
          v-if="group.type === 'message'"
          :msg="group.entry"
        />

        <!-- Activity block (grouped tools + thinking) -->
        <ActivityBlock
          v-else-if="group.type === 'activity'"
          :items="group.items"
        />

        <!-- Todo block -->
        <TodoBlock
          v-else-if="group.type === 'todo'"
          :entry="group.entry"
        />
      </template>
    </div>

    <!-- Interrupt bar -->
    <InterruptBar @resume="onResume" />

    <!-- Chat input (only shown when conversation is active) -->
    <ChatInput v-if="store.messages.length > 0" @send="onSend" @upload="onUpload" @stop="onStop" />

    <!-- Floating panel toggle bubble (top-right) -->
    <button
      v-if="store.processRunning || store.files.length > 0"
      v-show="!store.panelVisible"
      class="absolute top-16 right-5 z-50 w-10 h-10 rounded-xl
             bg-white text-text-secondary border border-border
             flex items-center justify-center cursor-pointer
             shadow-md hover:shadow-lg hover:text-text hover:border-text-muted
             transition-all duration-200"
      title="Open panel"
      @click="store.panelVisible = true"
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
        <polyline points="10 9 9 9 8 9"/>
      </svg>
    </button>
  </section>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useAppStore } from '@/stores/app'
import { getAgentColor } from '@/lib/utils'
import logoUrl from '@/assets/logo.svg'
import ChatMessage from './ChatMessage.vue'
import ActivityBlock from './ActivityBlock.vue'
import TodoBlock from './TodoBlock.vue'
import InterruptBar from './InterruptBar.vue'
import ChatInput from './ChatInput.vue'
import TypewriterText from './TypewriterText.vue'
import PromptInputBox from './PromptInputBox.vue'

const store = useAppStore()
const messagesEl = ref(null)
const landingText = ref('')
const landingTextarea = ref(null)
const landingFileInput = ref(null)

const emit = defineEmits(['send', 'upload', 'resume', 'stop'])

// Group consecutive tool + thinking entries into ActivityBlocks
const groupedMessages = computed(() => {
  const result = []
  let currentGroup = null

  for (const entry of store.messages) {
    const isActivity = entry.type === 'tool' || entry.type === 'thinking'

    if (isActivity) {
      if (!currentGroup) {
        currentGroup = { id: `group-${entry.id}`, type: 'activity', items: [] }
      }
      currentGroup.items.push(entry)
    } else {
      if (currentGroup) {
        result.push(currentGroup)
        currentGroup = null
      }
      result.push({ id: entry.id, type: entry.role ? 'message' : entry.type, entry })
    }
  }

  if (currentGroup) {
    result.push(currentGroup)
  }

  return result
})

// Landing page actions
function onLandingFileSelected(e) {
  const file = e.target.files?.[0]
  if (file) store.pendingFile = file
}

function onLandingSend() {
  const trimmed = landingText.value.trim()
  if (!trimmed && !store.pendingFile) return
  if (store.pendingFile) {
    emit('upload', trimmed)
  } else {
    emit('send', trimmed)
  }
  landingText.value = ''
}

// Auto-scroll on new messages
watch(
  () => store.messages.length,
  async () => {
    await nextTick()
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  },
)

// Also scroll when thinking chunks update
watch(
  () => store.thinkingBlocks.map(b => b.chunks.length),
  async () => {
    await nextTick()
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  },
  { deep: true },
)

function onSend(text) {
  emit('send', text)
}
function onUpload(text) {
  emit('upload', text)
}
function onResume(decision, message) {
  emit('resume', decision, message)
}
function onStop() {
  emit('stop')
}
</script>
