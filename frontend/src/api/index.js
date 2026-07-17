import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:5000', timeout: 15000 })

// 请求拦截器：自动带 Token
api.interceptors.request.use(c => {
  const t = localStorage.getItem('token')
  if (t) c.headers.Authorization = `Bearer ${t}`
  // 不要手动设 Content-Type，让浏览器自动设置（文件上传需要带 boundary）
  if (c.data instanceof FormData) {
    delete c.headers['Content-Type']
  }
  return c
})

// 响应拦截器：401 时跳转登录页
api.interceptors.response.use(
  r => r,
  e => {
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
