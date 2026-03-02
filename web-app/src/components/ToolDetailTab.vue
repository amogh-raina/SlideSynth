<template>
  <div class="flex flex-col flex-1 min-h-0" v-if="store.activeToolDetail">
    <!-- Tool header -->
    <div class="flex items-center gap-3 px-4 py-4 shrink-0 border-b border-border-light">
      <div
        class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
        :class="store.activeToolDetail.done ? 'bg-green-50 text-green-600' : 'bg-amber-50 text-amber-500'"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/>
        </svg>
      </div>

      <div class="flex-1 min-w-0">
        <div class="text-[12px] text-text-muted">
          {{ store.activeToolDetail.done ? 'Completed' : 'Running' }} Tool Execution
        </div>
        <div class="text-[14px] font-semibold text-text truncate">
          {{ store.activeToolDetail.text }}
        </div>
      </div>

      <div
        class="w-2.5 h-2.5 rounded-full shrink-0"
        :class="store.activeToolDetail.done ? 'bg-green-400' : 'bg-amber-400 animate-pulse'"
      />
    </div>

    <!-- Scrollable content -->
    <div class="flex-1 overflow-y-auto px-4 py-4 space-y-4">
      <!-- Request section -->
      <div>
        <h4 class="text-[12px] font-semibold text-text-muted uppercase tracking-wide mb-2">Request</h4>
        <div class="rounded-xl border border-border-light bg-bg-chat p-4">
          <div v-if="hasInput" class="space-y-2">
            <div
              v-for="(val, key) in store.activeToolDetail.input"
              :key="key"
              class="flex gap-2 text-[13px]"
            >
              <span class="text-text-muted font-medium shrink-0 min-w-[80px]">{{ key }}:</span>
              <span class="text-text break-all whitespace-pre-wrap">{{ formatValue(val) }}</span>
            </div>
          </div>
          <div v-else class="text-[13px] text-text-muted italic">No input parameters</div>
        </div>
      </div>

      <!-- Response section -->
      <div>
        <h4 class="text-[12px] font-semibold text-text-muted uppercase tracking-wide mb-2">Response</h4>
        <div class="rounded-xl border border-border-light bg-bg-chat p-4">
          <div
            v-if="store.activeToolDetail.output"
            class="text-[13px] text-text whitespace-pre-wrap break-words"
          >
            {{ store.activeToolDetail.output }}
          </div>
          <div
            v-else-if="!store.activeToolDetail.done"
            class="flex items-center gap-2 text-[13px] text-text-muted"
          >
            <div class="w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
            Waiting for response…
          </div>
          <div v-else class="text-[13px] text-text-muted italic">No response data</div>
        </div>
      </div>

      <!-- Metadata -->
      <div v-if="store.activeToolDetail.agent" class="text-[11px] text-text-muted">
        Agent: <span class="font-medium text-accent">{{ store.activeToolDetail.agent }}</span>
        <span class="mx-2">·</span>
        {{ store.activeToolDetail.time }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'

const store = useAppStore()

const hasInput = computed(() => {
  const input = store.activeToolDetail?.input
  return input && typeof input === 'object' && Object.keys(input).length > 0
})

function formatValue(val) {
  if (val === null || val === undefined) return 'null'
  if (typeof val === 'object') return JSON.stringify(val, null, 2)
  return String(val)
}
</script>
