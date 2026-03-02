<template>
  <div
    class="flex items-center gap-1.5 text-xs text-text-muted py-0.5 pl-10"
    :class="{ 'text-green': evt.evtType === 'tool_result' }"
  >
    <span class="text-[11px]">{{ evt.evtType === 'tool_call' ? '⚙' : '✓' }}</span>
    <span>{{ evt.agent }} →</span>
    <span class="font-medium text-accent">{{ evt.tool }}</span>
    <span
      v-if="evt.value"
      class="text-text-muted max-w-[200px] overflow-hidden text-ellipsis whitespace-nowrap"
    >
      {{ evt.value }}
    </span>
  </div>
</template>

<script setup>
defineProps({
  evt: { type: Object, required: true },
})
</script>
