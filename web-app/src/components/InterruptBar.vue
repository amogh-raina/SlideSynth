<template>
  <div v-if="store.interrupt" class="px-5 pb-2">
    <div class="bg-yellow-bg border border-amber-300 rounded-lg px-4 py-3.5 max-w-[80%] animate-fade-in">
      <div class="text-[13px] font-semibold text-amber-700 mb-2 flex items-center gap-1.5">
        ⚠ Agent waiting for approval
      </div>
      <div class="text-xs text-amber-800/80 mb-1.5">
        Action requires approval: {{ store.interrupt.action }}
      </div>
      <div class="flex gap-2 mt-2.5">
        <input
          v-model="feedback"
          type="text"
          placeholder="Optional feedback…"
          class="flex-1 px-3 py-2 border border-border rounded-md text-xs outline-none
                 focus:border-accent transition-colors"
        />
        <button
          class="px-4 py-2 bg-green text-white border-none rounded-md text-xs font-medium
                 hover:bg-green-600 transition-colors cursor-pointer"
          @click="approve"
        >
          ✓ Approve
        </button>
        <button
          class="px-4 py-2 bg-red text-white border-none rounded-md text-xs font-medium
                 hover:bg-red-600 transition-colors cursor-pointer"
          @click="reject"
        >
          ✗ Reject
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAppStore } from '@/stores/app'

const store = useAppStore()
const feedback = ref('')

const emit = defineEmits(['resume'])

function approve() {
  emit('resume', 'approve', feedback.value)
  feedback.value = ''
}

function reject() {
  emit('resume', 'reject', feedback.value)
  feedback.value = ''
}
</script>
