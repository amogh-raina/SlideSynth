<template>
  <div class="self-start max-w-[85%] animate-fade-in">
    <!-- Toggle header -->
    <div
      class="flex items-center gap-1.5 text-xs text-text-muted cursor-pointer py-1 select-none
             hover:text-text-secondary"
      @click="open = !open"
    >
      <span class="text-[10px] transition-transform duration-150"
            :class="open ? 'rotate-90' : ''">▶</span>
      <span v-if="!block.done"
            class="inline-block w-2.5 h-2.5 border-2 border-border border-t-accent rounded-full animate-spin" />
      <span>
        {{ block.done ? 'Thought for' : 'Thinking…' }}
        <span class="font-medium">{{ block.agent || 'SlideSynth' }}</span>
      </span>
    </div>

    <!-- Content -->
    <div
      v-show="open"
      class="text-[12.5px] text-text-secondary italic leading-relaxed pl-4.5
             max-h-50 overflow-y-auto whitespace-pre-wrap break-words"
    >
      {{ block.chunks }}
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  block: { type: Object, required: true },
})

const open = ref(true)

// Auto-close 3s after done
watch(
  () => props.block.done,
  (done) => {
    if (done) {
      setTimeout(() => {
        open.value = false
      }, 3000)
    }
  },
)
</script>
