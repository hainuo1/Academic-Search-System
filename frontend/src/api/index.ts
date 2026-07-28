import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 15000,
  withCredentials: true,
})

api.interceptors.request.use((c) => {
  const t = localStorage.getItem('token')
  if (t) c.headers.Authorization = `Bearer ${t}`
  if (c.data instanceof FormData) delete c.headers['Content-Type']
  return c
})

api.interceptors.response.use(
  (r) => r,
  (e) => {
    if (e.response && e.response.status === 401 && e.config.responseType !== 'blob') {
      localStorage.clear()
      if (window.location.pathname !== '/login' && window.location.pathname !== '/welcome') {
        window.location.href = '/welcome'
      }
    }
    return Promise.reject(e)
  }
)

export default api
