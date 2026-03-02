<template>
  <div class="self-start w-full max-w-[85%] animate-fade-in">
    <div class="border border-border-light rounded-xl overflow-hidden bg-bg-card">
      <div
        v-for="(item, idx) in items"
        :key="item.id"
        class="relative"
        :class="{ 'border-t border-border-light': idx > 0 }"
      >
        <!-- Vertical connecting line -->
        <div
          v-if="idx < items.length - 1"
          class="absolute left-[31px] w-[1.5px] bg-border-light z-0"
          :style="{
            top: item.type === 'tool' ? '44px' : '36px',
            bottom: '-1px',
          }"
        />

        <!-- Tool event row -->
        <div
          v-if="item.type === 'tool'"
          class="flex items-center gap-3 px-4 py-3 cursor-pointer
                 hover:bg-bg-chat/50 transition-colors relative z-10"
          @click="onToolClick(item)"
        >
          <!-- Icon -->
          <div
            class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0"
            :class="item.done
              ? 'bg-green-bg text-green'
              : 'bg-yellow-bg text-orange'"
          >
            <!-- Document icon for read/extract tools -->
            <svg v-if="isDocTool(item.tool)" width="14" height="14" viewBox="0 0 24 24"
                 fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
            <!-- Wrench icon for other tools -->
            <svg v-else width="14" height="14" viewBox="0 0 24 24"
                 fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/>
            </svg>
          </div>

          <!-- Label + detail -->
          <div class="flex items-center gap-1.5 flex-1 min-w-0">
            <span class="text-[13px] font-medium shrink-0"
                  :class="item.done ? 'text-text' : 'text-text-muted'">
              {{ toolLabel(item.tool) }}
            </span>
            <span v-if="getToolDetail(item)"
                  class="text-[13px] text-text-muted shrink-0">│</span>
            <span v-if="getToolDetail(item)"
                  class="text-[13px] text-text-secondary truncate">
              {{ getToolDetail(item) }}
            </span>

            <!-- Running spinner -->
            <span v-if="!item.done"
                  class="inline-block w-3 h-3 border-2 border-border border-t-accent
                         rounded-full animate-spin shrink-0 ml-1" />
          </div>

          <!-- Chevron -->
          <svg class="w-4 h-4 text-text-muted shrink-0"
               viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </div>

        <!-- Thinking row -->
        <div
          v-else-if="item.type === 'thinking'"
          class="relative z-10"
        >
          <!-- Toggle header -->
          <div
            class="flex items-center gap-3 px-4 py-3 cursor-pointer select-none
                   hover:bg-bg-chat/50 transition-colors"
            @click="toggle(item.blockId)"
          >
            <!-- Bullet (aligned with tool icons) -->
            <div class="w-7 h-7 flex items-center justify-center shrink-0">
              <span class="w-2 h-2 rounded-full bg-text-muted" />
            </div>

            <span class="text-[13px] font-medium text-text">Think</span>

            <!-- Duration badge -->
            <span v-if="block(item.blockId)?.duration"
                  class="text-[11px] text-text-muted bg-bg-chat px-1.5 py-0.5 rounded">
              {{ block(item.blockId).duration }}s
            </span>
            <!-- Spinner while thinking -->
            <span v-else-if="!block(item.blockId)?.done"
                  class="inline-block w-3 h-3 border-2 border-border border-t-accent
                         rounded-full animate-spin" />

            <div class="flex-1" />

            <!-- Expand/collapse chevron -->
            <svg class="w-4 h-4 text-text-muted transition-transform duration-200 shrink-0"
                 :class="{ '-rotate-90': !isExpanded(item.blockId) }"
                 viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 9l6 6 6-6"/>
            </svg>
          </div>

          <!-- Thinking content -->
          <div
            v-show="isExpanded(item.blockId)"
            class="px-4 pb-3 pl-[52px] text-[12.5px] text-text-secondary leading-relaxed
                   max-h-52 overflow-y-auto whitespace-pre-wrap break-words"
          >
            {{ block(item.blockId)?.chunks }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
import { useAppStore } from '@/stores/app'

const props = defineProps({
  items: { type: Array, required: true },
})

const store = useAppStore()
const expanded = reactive({})

// ── Thinking helpers ──

function block(blockId) {
  return store.thinkingBlocks.find(b => b.id === blockId)
}

function isExpanded(blockId) {
  return expanded[blockId] !== false // default expanded
}

function toggle(blockId) {
  expanded[blockId] = expanded[blockId] === false
}

// Auto-collapse thinking 3s after done
watch(
  () => store.thinkingBlocks.map(b => b.done),
  () => {
    for (const item of props.items) {
      if (item.type !== 'thinking') continue
      const b = block(item.blockId)
      if (b?.done && expanded[item.blockId] !== false) {
        setTimeout(() => { expanded[item.blockId] = false }, 3000)
      }
    }
  },
  { deep: true },
)

// ── Tool helpers ──

function isDocTool(tool) {
  return /parse_pdf|enhanced_extract|read/i.test(tool)
}

const toolLabels = {
  parse_pdf: 'Read',
  enhanced_extract: 'Extract',
  generate_slide_html: 'Generate',
  combine_presentation: 'Build',
  quality_check: 'Quality Check',
  verify_plan: 'Verify',
  export_to_pdf: 'Export',
  resolve_asset: 'Resolve Asset',
  copy_asset_to_slide: 'Copy Asset',
  list_assets: 'List Assets',
  switch_template: 'Switch Template',
}

function toolLabel(name) {
  return toolLabels[name] || name.split('_').map(w => w[0].toUpperCase() + w.slice(1)).join(' ')
}

function getToolDetail(item) {
  const inp = item.input
  if (!inp || typeof inp !== 'object') return ''
  if (inp.pdf_path) return inp.pdf_path.split('/').pop()
  if (inp.slide_number != null) return `Slide ${inp.slide_number}`
  if (inp.template_name) return inp.template_name
  if (inp.asset_path) return inp.asset_path.split('/').pop()
  if (inp.project_id) return inp.project_id.slice(0, 8) + '…'
  return ''
}

function onToolClick(item) {
  if (item.logId != null) {
    const logEntry = store.processLog.find(e => e.id === item.logId)
    if (logEntry) {
      store.openToolDetail(logEntry)
      if (!store.panelVisible) store.panelVisible = true
      return
    }
  }
}
</script>
