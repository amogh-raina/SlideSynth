<template>
  <div class="select-none font-mono">
    <!-- Folder -->
    <div v-if="node.children">
      <div
        class="group relative flex items-center gap-2 py-1.5 px-2.5 rounded-md cursor-pointer
               transition-all duration-200 ease-out hover:bg-gray-100"
        @click="open = !open"
      >
        <!-- Tree lines logic omitted for simplicity unless we pass depth properly, but we have depth in props.node.depth -->
        <!-- Folder indicator -->
        <div class="flex items-center justify-center w-4 h-4 transition-transform duration-200"
             :class="{ 'rotate-90': open }">
          <svg width="6" height="8" viewBox="0 0 6 8" fill="none" class="text-gray-400 group-hover:text-gray-600 transition-colors">
            <path d="M1 1L5 4L1 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
        
        <!-- Folder Icon -->
        <div class="flex items-center justify-center w-5 h-5 rounded transition-all duration-200 text-blue-400 group-hover:scale-110">
          <svg width="16" height="14" viewBox="0 0 16 14" fill="currentColor">
            <path d="M1.5 1C0.671573 1 0 1.67157 0 2.5V11.5C0 12.3284 0.671573 13 1.5 13H14.5C15.3284 13 16 12.3284 16 11.5V4.5C16 3.67157 15.3284 3 14.5 3H8L6.5 1H1.5Z" />
          </svg>
        </div>

        <span class="text-[13.5px] transition-colors duration-200 text-gray-700 group-hover:text-black">{{ node.name }}</span>
      </div>

      <div v-show="open" class="pl-4 border-l border-gray-200 ml-4 mt-0.5">
        <FileNode
          v-for="child in node.children"
          :key="child.path"
          :node="child"
          :active-path="activePath"
          @preview="$emit('preview', $event)"
        />
      </div>
    </div>

    <!-- File -->
    <div
      v-else
      class="group relative flex items-center gap-2 py-1.5 px-2.5 rounded-md cursor-pointer text-[13.5px]
             transition-all duration-200 ease-out hover:bg-gray-100"
      :class="activePath === node.path ? 'bg-blue-50/50' : ''"
      @click="$emit('preview', node.path)"
    >
      <div class="flex items-center justify-center w-4 h-4 ml-1">
        <span class="text-[12px] font-bold transition-opacity duration-200 group-hover:scale-110" :class="fileVisual.color">
          {{ isEmoji(fileVisual.icon) ? '' : fileVisual.icon }}
        </span>
      </div>
      
      <div class="flex items-center justify-center w-5 h-5 rounded transition-all duration-200 opacity-80 group-hover:opacity-100 group-hover:scale-110" :class="fileVisual.color">
        <svg v-if="!isEmoji(fileVisual.icon)" width="14" height="16" viewBox="0 0 14 16" fill="currentColor">
          <path d="M1.5 0C0.671573 0 0 0.671573 0 1.5V14.5C0 15.3284 0.671573 16 1.5 16H12.5C13.3284 16 14 15.3284 14 14.5V4.5L9.5 0H1.5Z" />
          <path d="M9 0V4.5H14" fill="currentColor" fill-opacity="0.5" />
        </svg>
        <span v-else class="text-sm shadow-none bg-transparent flex items-center justify-center -ml-2 -mt-1">{{ fileVisual.icon }}</span>
      </div>

      <span class="whitespace-nowrap overflow-hidden text-ellipsis flex-1 text-gray-600 group-hover:text-black transition-colors"
            :class="activePath === node.path ? 'font-semibold text-blue-600' : ''">
        {{ node.name }}
      </span>
      <span v-if="node.size" class="text-[11px] text-gray-400 shrink-0 ml-auto">{{ node.size }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getFileIcon } from '@/lib/utils'

const props = defineProps({
  node: { type: Object, required: true },
  activePath: { type: String, default: null },
})

defineEmits(['preview'])

const open = ref(props.node.depth < 1)
const fileVisual = computed(() => getFileIcon(props.node.name))

const isEmoji = (icon) => {
  return ['📄', '📕', '🖼', '📋'].includes(icon)
}
</script>
