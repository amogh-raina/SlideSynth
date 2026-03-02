<template>
  <div class="relative w-full max-w-[800px] mx-auto">
    <!-- File Display -->
    <div v-if="hasFile" class="flex flex-wrap gap-2 pb-2 transition-all duration-300">
      <div class="relative group bg-[#2A2B2F] rounded-xl flex items-center p-2 pr-8 border border-[#444]">
        <div class="flex items-center justify-center w-8 h-8 rounded-lg bg-[#3A3B40] text-red-400 mr-2">
           <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
        </div>
        <span class="text-sm text-gray-200 truncate max-w-[200px] font-medium">{{ fileName }}</span>
        <button
          @click.stop="$emit('clearFile')"
          class="absolute top-1/2 right-2 -translate-y-1/2 rounded-full p-1 opacity-70 hover:opacity-100 hover:bg-[#444] transition-all cursor-pointer"
        >
          <X class="h-3.5 w-3.5 text-white" />
        </button>
      </div>
    </div>

    <div
      class="rounded-[24px] border border-[#444] bg-[#1F2023] p-2.5 shadow-[0_8px_30px_rgba(0,0,0,0.12)] transition-all duration-300"
      :class="{ 'border-red-500/70': isRunning }"
    >
      <!-- Textarea -->
      <div class="relative opacity-100 transition-all duration-300 flex items-center">
        <textarea
          ref="textareaRef"
          :value="modelValue"
          @input="onInput"
          @keydown="onKeyDown"
          :disabled="isRunning"
          :placeholder="placeholder"
          class="flex w-full rounded-md border-none bg-transparent px-3 py-2 text-[15px] text-gray-100 placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-0 disabled:cursor-not-allowed disabled:opacity-50 min-h-[44px] max-h-48 resize-none scrollbar-thin scrollbar-thumb-[#444444] scrollbar-track-transparent leading-relaxed"
          rows="1"
        ></textarea>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-between gap-2 p-0 pt-2 px-1">
        <!-- left group -->
        <div class="flex items-center gap-1">
          <!-- Upload PDF action -->
          <button
            type="button"
            @click="$emit('upload')"
            class="flex h-8 w-8 text-[#9CA3AF] cursor-pointer items-center justify-center rounded-full transition-colors hover:bg-[#3A3A40] hover:text-[#D1D5DB]"
            title="Attach PDF"
            :disabled="isRunning"
          >
            <Paperclip class="h-4 w-4" />
          </button>
          
          <div class="flex items-center ml-1">
            <!-- Canvas button triggers the right panel toggle -->
            <button
              type="button"
              @click="handleCanvasToggle"
              class="rounded-full transition-all flex items-center gap-1 px-2 py-1 border h-8 bg-transparent border-transparent text-[#9CA3AF] hover:text-[#D1D5DB]"
            >
              <div class="w-5 h-5 flex items-center justify-center shrink-0">
                <FolderCode class="w-[15px] h-[15px] text-inherit" />
              </div>
              <transition name="fade-width">
                <span class="text-xs font-medium overflow-hidden whitespace-nowrap">
                  Canvas
                </span>
              </transition>
            </button>
          </div>
        </div>

        <!-- right group / send button -->
        <button
          v-if="isRunning"
          type="button"
          @click="$emit('stop')"
          class="h-8 w-8 rounded-[10px] flex items-center justify-center bg-red-500/20 hover:bg-red-500/30 text-red-500 transition-colors"
          title="Stop"
        >
          <Square class="h-3.5 w-3.5 fill-current" />
        </button>
        <button
          v-else
          type="button"
          @click="submit"
          :disabled="!hasContent"
          class="h-8 w-8 rounded-[10px] flex items-center justify-center transition-all duration-200"
          :class="hasContent ? 'bg-white hover:bg-gray-200 text-[#1F2023] scale-100 shadow-sm cursor-pointer' : 'bg-[#2A2B2F] text-[#666] cursor-default'"
          title="Send"
        >
          <ArrowUp class="h-4 w-4" :stroke-width="2.5" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ArrowUp, Paperclip, Square, X, FolderCode } from 'lucide-vue-next'

const props = defineProps({
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: 'Type your message here...' },
  hasFile: { type: Boolean, default: false },
  fileName: { type: String, default: '' },
  isRunning: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'send', 'upload', 'clearFile', 'stop', 'togglePanel'])

const textareaRef = ref(null)

const hasContent = computed(() => {
  return props.modelValue.trim().length > 0 || props.hasFile
})

function onInput(e) {
  emit('update:modelValue', e.target.value)
  autoResize()
}

function onKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    if (hasContent.value && !props.isRunning) {
      submit()
    }
  }
}

function submit() {
  if (!hasContent.value || props.isRunning) return
  // reset height
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
  }
  emit('send')
}

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 192) + 'px'
}

function handleCanvasToggle() {
  emit('togglePanel')
}

watch(() => props.modelValue, () => {
  nextTick(autoResize)
})
</script>

<style scoped>
.fade-width-enter-active,
.fade-width-leave-active {
  transition: all 0.25s ease-out;
}
.fade-width-enter-from,
.fade-width-leave-to {
  width: 0;
  opacity: 0;
  margin-left: 0;
}
.fade-width-enter-to,
.fade-width-leave-from {
  width: auto;
  opacity: 1;
  margin-left: 4px;
}
</style>
