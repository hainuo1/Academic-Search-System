import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const userId = ref(localStorage.getItem('userId') || '')
  const isLoggedIn = computed(() => !!token.value)

  function login(t: string, u: string, id: string) {
    token.value = t; username.value = u; userId.value = String(id)
    localStorage.setItem('token', t); localStorage.setItem('username', u); localStorage.setItem('userId', String(id))
  }
  function logout() { token.value = ''; username.value = ''; userId.value = ''; localStorage.clear() }
  return { token, username, userId, isLoggedIn, login, logout }
})
