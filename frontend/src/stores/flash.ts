import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useFlashStore = defineStore('flash', () => {
  const message = ref('')
  const type = ref<'success' | 'warning' | 'error' | 'info'>('info')
  let timer: ReturnType<typeof setTimeout> | null = null

  function show(msg: string, t: 'success' | 'warning' | 'error' | 'info' = 'info') {
    if (timer) clearTimeout(timer)
    message.value = msg; type.value = t
    timer = setTimeout(() => { message.value = '' }, 4000)
  }
  return { message, type, show }
})
