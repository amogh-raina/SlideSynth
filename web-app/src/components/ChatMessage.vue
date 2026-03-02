<template>
  <div
    class="flex gap-3 max-w-[85%] animate-fade-in"
    :class="msg.role === 'user' ? 'self-end flex-row-reverse' : 'self-start'"
  >
    <!-- Avatar -->
    <div
      class="w-8 h-8 rounded-full flex items-center justify-center text-[13px] font-semibold shrink-0 text-white"
      :style="{ background: msg.role === 'user' ? 'var(--color-accent)' : agentColor }"
    >
      {{ msg.role === 'user' ? 'U' : avatarLetter }}
    </div>

    <div>
      <!-- Agent label -->
      <div v-if="msg.agent && msg.role !== 'user'"
           class="text-[12px] font-medium text-text-muted mb-1 ml-1">
        {{ msg.agent }}
      </div>

      <!-- Bubble -->
      <div
        class="px-4 py-3 rounded-[20px] text-[14.5px] leading-relaxed shadow-sm w-full"
        :class="msg.role === 'user'
          ? 'bg-accent text-white rounded-br-sm'
          : 'bg-white border border-border rounded-bl-sm text-gray-800'"
      >
        <div v-if="msg.html" class="prose-msg" :class="{'prose-msg-user': msg.role === 'user'}" v-html="msg.content" />
        <div v-else class="prose-msg" :class="{'prose-msg-user': msg.role === 'user'}" v-html="rendered" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, nextTick, watch } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import { getAgentColor } from '@/lib/utils'

// Setup marked to use highlight.js
marked.setOptions({
  highlight: function(code, lang) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language }).value
  },
  langPrefix: 'hljs language-',
})

const props = defineProps({
  msg: { type: Object, required: true },
})

const agentColor = computed(() => getAgentColor(props.msg.agent))
const avatarLetter = computed(() =>
  props.msg.agent ? props.msg.agent[0].toUpperCase() : 'S',
)

const rendered = computed(() => {
  if (props.msg.html) return props.msg.content
  // Use marked for markdown rendering
  return marked.parse(props.msg.content || '', { breaks: true })
})
</script>
