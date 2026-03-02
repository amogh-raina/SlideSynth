<template>
  <span :class="className">
    {{ displayText }}
    <span class="animate-pulse">{{ cursor }}</span>
  </span>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'

const props = defineProps({
  text: {
    type: [String, Array],
    required: true
  },
  speed: {
    type: Number,
    default: 100
  },
  cursor: {
    type: String,
    default: "|"
  },
  loop: {
    type: Boolean,
    default: false
  },
  deleteSpeed: {
    type: Number,
    default: 50
  },
  delay: {
    type: Number,
    default: 1500
  },
  className: {
    type: String,
    default: ""
  }
})

const displayText = ref("")
const currentIndex = ref(0)
const isDeleting = ref(false)
const textArrayIndex = ref(0)
let timeoutId = null

const textArray = computed(() => Array.isArray(props.text) ? props.text : [props.text])
const currentText = computed(() => textArray.value[textArrayIndex.value] || "")


const tick = () => {
  if (!currentText.value) return

  if (!isDeleting.value) {
    if (currentIndex.value < currentText.value.length) {
      displayText.value += currentText.value[currentIndex.value]
      currentIndex.value++
      timeoutId = setTimeout(tick, props.speed)
    } else if (props.loop || textArrayIndex.value < textArray.value.length - 1) {
      // Pause at the end before deleting or moving to next if not looping
      timeoutId = setTimeout(() => {
        isDeleting.value = true
        tick()
      }, props.delay)
    }
  } else {
    if (displayText.value.length > 0) {
      displayText.value = displayText.value.slice(0, -1)
      timeoutId = setTimeout(tick, props.deleteSpeed)
    } else {
      isDeleting.value = false
      currentIndex.value = 0
      textArrayIndex.value = (textArrayIndex.value + 1) % textArray.value.length
      // Once empty, if not looping and at first index, stop.
      if (!props.loop && textArrayIndex.value === 0) {
          return;
      }
      tick()
    }
  }
}

onMounted(() => {
  tick()
})

onUnmounted(() => {
  if (timeoutId) clearTimeout(timeoutId)
})

watch(() => props.text, () => {
  isDeleting.value = false
  currentIndex.value = 0
  textArrayIndex.value = 0
  displayText.value = ""
  if (timeoutId) clearTimeout(timeoutId)
  tick()
})
</script>
