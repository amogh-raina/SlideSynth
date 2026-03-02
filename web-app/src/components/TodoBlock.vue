<template>
  <div class="self-start bg-bg-card border border-border-light rounded-lg px-4 py-3 max-w-[75%] animate-fade-in">
    <div class="text-xs font-semibold text-text-secondary mb-2 flex items-center gap-1.5">
      <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M9 11l3 3L22 4" /><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11" />
      </svg>
      To-dos ({{ completed }}/{{ entry.todos.length }})
    </div>
    <div
      v-for="(t, i) in entry.todos"
      :key="i"
      class="flex items-center gap-2 text-[13px] py-0.5"
      :class="{
        'text-text-muted line-through': t.status === 'completed',
        'text-accent font-medium': t.status === 'in_progress',
      }"
    >
      <div
        class="w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0 text-[10px]"
        :class="t.status === 'completed'
          ? 'bg-green border-green text-white'
          : t.status === 'in_progress'
            ? 'border-accent bg-accent-light'
            : 'border-border'"
      >
        {{ t.status === 'completed' ? '✓' : t.status === 'in_progress' ? '●' : '' }}
      </div>
      <span>{{ t.content }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  entry: { type: Object, required: true },
})

const completed = computed(() =>
  props.entry.todos.filter(t => t.status === 'completed').length,
)
</script>
