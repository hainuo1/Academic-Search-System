import { defineStore } from 'pinia'
import { ref } from 'vue'
export const useFlashStore = defineStore('flash', () => {
  const message = ref(''); const type = ref('info')
  function show(m, t = 'info') { message.value = m; type.value = t; setTimeout(() => { message.value = '' }, 4000) }
  return { message, type, show }
})