<template>
  <div class="flex flex-col flex-1 min-h-0">
    <!-- Status bar -->
    <div class="flex items-center gap-3 px-4 py-3 shrink-0 border-b border-border-light">
      <div class="flex items-center gap-2">
        <div
          class="w-2 h-2 rounded-full"
          :class="store.processRunning ? 'bg-green-500 animate-pulse' : 'bg-gray-300'"
        />
        <span class="text-[13px] font-medium text-text">
          {{ store.processRunning ? 'Running' : store.processStatus === 'Completed' ? 'Completed' : 'Idle' }}
        </span>
      </div>
      <div class="flex-1" />
      <div v-if="store.slideCount > 0" class="flex gap-3 text-[12px] text-text-muted">
        <span>{{ store.slideCount }} slides</span>
        <span>{{ store.imageCount }} images</span>
        <span>{{ store.tableCount }} tables</span>
      </div>
    </div>

    <!-- Card list -->
    <div ref="scrollEl" class="flex-1 overflow-y-auto px-3 py-3 space-y-2">
      <!-- Empty state -->
      <div v-if="!store.processLog.length" class="flex flex-col items-center justify-center h-full text-text-muted">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="mb-3 opacity-40">
          <path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/>
        </svg>
        <p class="text-[13px]">Waiting for process…</p>
        <p class="text-[12px] opacity-60 mt-1">Upload a PDF to start.</p>
      </div>

      <!-- Log entries -->
      <template v-for="entry in store.processLog" :key="entry.id">
        <!-- Tool call card -->
        <div
          v-if="entry.type === 'tool_call'"
          class="group flex items-center gap-3 px-3.5 py-3 rounded-xl border border-border-light
                 bg-white hover:border-border hover:shadow-sm transition-all cursor-pointer"
          @click="store.openToolDetail(entry)"
        >
          <!-- Icon -->
          <div
            class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
            :class="entry.done ? 'bg-green-50 text-green-600' : 'bg-amber-50 text-amber-500'"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/>
            </svg>
          </div>

          <!-- Label -->
          <div class="flex-1 min-w-0">
            <div class="text-[12px] text-text-muted">
              {{ entry.done ? 'Completed' : 'Running' }} Tool Execution
            </div>
            <div class="text-[13px] font-semibold text-text truncate">
              {{ entry.text }}
            </div>
          </div>

          <!-- Status dot -->
          <div
            class="w-2.5 h-2.5 rounded-full shrink-0"
            :class="entry.done ? 'bg-green-400' : 'bg-amber-400 animate-pulse'"
          />

          <!-- Chevron -->
          <svg
            class="w-4 h-4 text-text-muted opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
          >
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </div>

        <!-- Agent / status entries (inline) -->
        <div
          v-else
          class="flex items-center gap-2.5 px-3.5 py-2 text-[12px]"
        >
          <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="dotColor(entry.type)" />
          <span class="text-text-muted">{{ entry.time }}</span>
          <span v-if="entry.agent" class="text-accent font-medium">{{ entry.agent }}</span>
          <span :class="textColor(entry.type)">{{ entry.text }}</span>
        </div>
      </template>
    </div>

    <!-- Todos (collapsible) -->
    <div v-if="store.todos.length" class="border-t border-border-light shrink-0">
      <button
        class="w-full flex items-center gap-2 px-4 py-2.5 text-[12px] font-medium text-text-muted
               bg-transparent border-none cursor-pointer hover:text-text transition-colors text-left"
        @click="todosOpen = !todosOpen"
      >
        <svg
          class="w-3 h-3 transition-transform duration-150"
          :class="{ 'rotate-90': todosOpen }"
          viewBox="0 0 24 24" fill="currentColor"
        >
          <path d="M8 5l8 7-8 7z"/>
        </svg>
        Tasks ({{ store.todos.filter(t => t.status === 'completed').length }}/{{ store.todos.length }})
      </button>
      <div v-show="todosOpen" class="px-4 pb-3 space-y-1.5">
        <div
          v-for="(t, i) in store.todos"
          :key="i"
          class="flex items-center gap-2 text-[12.5px]"
          :class="{
            'text-text-muted line-through opacity-60': t.status === 'completed',
            'text-accent': t.status === 'in_progress',
            'text-text': t.status !== 'completed' && t.status !== 'in_progress',
          }"
        >
          <span class="text-[11px] shrink-0">
            {{ t.status === 'completed' ? '✓' : t.status === 'in_progress' ? '●' : '○' }}
          </span>
          <span>{{ t.content }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useAppStore } from '@/stores/app'

const store = useAppStore()
const scrollEl = ref(null)
const todosOpen = ref(true)

function dotColor(type) {
  const m = {
    agent: 'bg-blue-400',
    success: 'bg-green-400',
    info: 'bg-gray-300',
    warn: 'bg-amber-400',
    error: 'bg-red-400',
    tool_result: 'bg-green-400',
  }
  return m[type] || 'bg-gray-300'
}

function textColor(type) {
  const m = {
    agent: 'text-text',
    success: 'text-green-600',
    info: 'text-text-muted',
    warn: 'text-amber-600',
    error: 'text-red-500',
    tool_result: 'text-green-600',
  }
  return m[type] || 'text-text-muted'
}

// Auto-scroll
watch(
  () => store.processLog.length,
  async () => {
    await nextTick()
    if (scrollEl.value) {
      scrollEl.value.scrollTop = scrollEl.value.scrollHeight
    }
  },
)
</script>
