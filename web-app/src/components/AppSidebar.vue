<template>
  <nav
    class="bg-bg-sidebar border-r border-border flex flex-col shrink-0 transition-all duration-200 overflow-hidden"
    :style="{ width: collapsed ? '56px' : sidebarWidth + 'px' }"
  >
    <!-- Logo + sidebar toggle -->
    <div class="flex items-center shrink-0"
         :class="collapsed ? 'justify-center px-0 py-5' : 'px-4 py-5 gap-3'">
      <img :src="logoUrl" :class="collapsed ? 'w-8 h-8' : 'w-9 h-9'" alt="SlideSynth" class="shrink-0" />
      <!-- Sidebar toggle icon (top-right of sidebar header) -->
      <button
        v-if="!collapsed"
        class="ml-auto bg-transparent border-none text-text-muted cursor-pointer p-1.5 rounded-md
               hover:bg-bg-chat hover:text-text transition-colors"
        title="Toggle sidebar"
        @click="$emit('toggle-collapse')"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <rect x="3" y="3" width="18" height="18" rx="3"/>
          <line x1="9" y1="3" x2="9" y2="21"/>
        </svg>
      </button>
    </div>

    <!-- New Task (sleek style, not a blue block) -->
    <div :class="collapsed ? 'px-1.5 flex justify-center' : 'px-3'">
      <button
        v-if="collapsed"
        class="w-10 h-10 p-0 bg-transparent text-text border-none rounded-lg
               flex items-center justify-center hover:bg-bg-chat transition-colors cursor-pointer"
        title="New Project"
        @click="$emit('newProject')"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <circle cx="12" cy="12" r="9"/>
          <path d="M12 8v8M8 12h8"/>
        </svg>
      </button>
      <button
        v-else
        class="w-full flex items-center gap-3 px-3 py-2.5 bg-transparent text-text border-none
               rounded-lg text-[14px] font-medium hover:bg-bg-chat transition-colors cursor-pointer"
        @click="$emit('newProject')"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="text-text-secondary shrink-0">
          <circle cx="12" cy="12" r="9"/>
          <path d="M12 8v8M8 12h8"/>
        </svg>
        New Task
      </button>
    </div>

    <!-- Expand button (only when collapsed) -->
    <button
      v-if="collapsed"
      class="mx-auto mt-2 bg-transparent border-none text-text-muted cursor-pointer p-1.5
             rounded-md hover:bg-bg-chat hover:text-text transition-colors"
      title="Expand sidebar"
      @click="$emit('toggle-collapse')"
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
        <rect x="3" y="3" width="18" height="18" rx="3"/>
        <line x1="9" y1="3" x2="9" y2="21"/>
      </svg>
    </button>

    <!-- History -->
    <div v-if="!collapsed" class="px-3 pt-4 pb-1.5 flex-1 overflow-y-auto">
      <div class="text-[11.5px] font-semibold text-text-muted uppercase tracking-wider px-3 py-2 pb-1.5 flex items-center gap-1">
        Task History
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="opacity-50">
          <path d="M6 9l6 6 6-6"/>
        </svg>
      </div>
      <div
        v-for="proj in store.projects"
        :key="proj.id"
        class="flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-[14px] cursor-pointer
               transition-colors whitespace-nowrap overflow-hidden text-ellipsis"
        :class="proj.active
          ? 'bg-bg-chat text-text font-medium'
          : 'text-text-secondary hover:bg-bg-chat'"
        @click="$emit('switchProject', proj.id)"
      >
        {{ proj.name }}
        <span
          v-if="proj.hasError"
          class="w-2 h-2 rounded-full bg-red ml-auto shrink-0"
        />
      </div>
    </div>

    <!-- Collapsed: history dots only -->
    <div v-if="collapsed" class="flex flex-col items-center gap-1.5 mt-3 flex-1 overflow-y-auto px-1">
      <div
        v-for="proj in store.projects"
        :key="proj.id"
        class="w-9 h-9 rounded-lg flex items-center justify-center cursor-pointer transition-colors"
        :class="proj.active ? 'bg-bg-chat text-text' : 'text-text-muted hover:bg-bg-chat'"
        :title="proj.name"
        @click="$emit('switchProject', proj.id)"
      >
        <span
          class="w-2 h-2 rounded-full"
          :class="proj.active ? 'bg-green' : 'bg-text-muted'"
        />
      </div>
    </div>

    <!-- Footer -->
    <div class="mt-auto border-t border-border-light text-[11.5px] text-text-muted"
         :class="collapsed ? 'px-1 py-3 text-center' : 'px-4 py-3'">
      <span v-if="collapsed" title="SlideSynth v0.1">v0.1</span>
      <span v-else>SlideSynth v0.1 · PDF → Slides</span>
    </div>
  </nav>
</template>

<script setup>
import { useAppStore } from '@/stores/app'
import logoUrl from '@/assets/logo.svg'

defineProps({
  sidebarWidth: { type: Number, default: 240 },
  collapsed: { type: Boolean, default: false },
})

defineEmits(['newProject', 'switchProject', 'toggle-collapse'])

const store = useAppStore()
</script>
