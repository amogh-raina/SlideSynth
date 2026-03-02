<template>
  <div
    class="resize-handle"
    @mousedown.prevent="onMouseDown"
  />
</template>

<script setup>
const props = defineProps({
  side: { type: String, required: true }, // 'left' or 'right'
  getWidth: { type: Function, required: true },
})

const emit = defineEmits(['resize'])

function onMouseDown(e) {
  const startX = e.clientX
  const startW = props.getWidth()
  const handle = e.currentTarget
  handle.classList.add('dragging')
  document.body.classList.add('resizing')

  function onMove(ev) {
    const dx = ev.clientX - startX
    let w
    if (props.side === 'left') {
      w = Math.max(140, Math.min(400, startW + dx))
    } else {
      w = Math.max(280, Math.min(800, startW - dx))
    }
    emit('resize', w)
  }

  function onUp() {
    handle.classList.remove('dragging')
    document.body.classList.remove('resizing')
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
  }

  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}
</script>
