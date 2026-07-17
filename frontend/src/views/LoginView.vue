<template>
<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-100 via-blue-50 to-indigo-50 py-12 px-4">
  <div class="w-full max-w-5xl bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden flex flex-col md:flex-row border border-white/50">

    <!-- 左栏：品牌区 -->
    <div class="w-full md:w-2/5 bg-gradient-to-br from-slate-900 via-blue-950 to-indigo-950 p-8 md:p-10 flex flex-col justify-between relative overflow-hidden">
      <div class="absolute -top-32 -right-32 w-80 h-80 bg-indigo-500/20 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-32 -left-32 w-80 h-80 bg-blue-400/10 rounded-full blur-3xl"></div>
      <div class="absolute top-1/3 right-0 w-2 h-2 bg-white/40 rounded-full"></div>
      <div class="absolute top-1/4 right-1/4 w-3 h-3 bg-white/20 rounded-full"></div>
      <div class="absolute bottom-1/3 left-1/4 w-1.5 h-1.5 bg-white/30 rounded-full"></div>

      <div class="relative z-10">
        <div class="flex items-center gap-3 text-white/90 mb-10">
          <div class="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center backdrop-blur-sm">
            <i class="fa fa-book text-white text-lg"></i>
          </div>
          <span class="text-base font-semibold tracking-wide">学术文献检索</span>
        </div>
        <h2 class="text-4xl font-bold text-white leading-tight tracking-tight">欢迎回来</h2>
        <p class="text-indigo-200/80 text-sm mt-3 leading-relaxed max-w-xs">登录您的账户，继续您的学术探索之旅。</p>
      </div>

      <div class="relative z-10 mt-8">
        <div class="grid grid-cols-3 gap-3 pt-6 border-t border-white/10">
          <div class="text-center group cursor-default">
            <div class="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center mx-auto mb-2 group-hover:bg-white/20 transition-colors">
              <i class="fa fa-search text-yellow-300 text-sm"></i>
            </div>
            <span class="text-xs text-indigo-200/80">智能检索</span>
          </div>
          <div class="text-center group cursor-default">
            <div class="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center mx-auto mb-2 group-hover:bg-white/20 transition-colors">
              <i class="fa fa-star text-yellow-300 text-sm"></i>
            </div>
            <span class="text-xs text-indigo-200/80">收藏管理</span>
          </div>
          <div class="text-center group cursor-default">
            <div class="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center mx-auto mb-2 group-hover:bg-white/20 transition-colors">
              <i class="fa fa-link text-yellow-300 text-sm"></i>
            </div>
            <span class="text-xs text-indigo-200/80">引用分析</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右栏：登录表单 -->
    <div class="w-full md:w-3/5 p-8 md:p-14 flex items-center justify-center bg-white/50">
      <div class="w-full max-w-sm">
        <div class="md:hidden text-center mb-8">
          <h2 class="text-3xl font-bold text-slate-800">登录</h2>
          <p class="text-slate-500 text-sm mt-1">登录您的账户，继续学术探索</p>
        </div>

        <div v-if="err" class="mb-6 bg-red-50 border border-red-100 text-red-600 px-4 py-3 rounded-2xl flex items-center text-sm backdrop-blur-sm">
          <i class="fa fa-exclamation-circle mr-2.5 flex-shrink-0"></i><span>{{ err }}</span>
        </div>

        <form @submit.prevent="go" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-slate-600 mb-2" for="username">用户名</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400"><i class="fa fa-user-o"></i></span>
              <input v-model="un" type="text" id="username"
                class="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none"
                placeholder="请输入用户名" required>
            </div>
          </div>

          <div>
            <div class="flex justify-between items-center mb-2">
              <label class="block text-sm font-medium text-slate-600" for="password">密码</label>
              <router-link to="/forgot_password" class="text-xs text-indigo-500 hover:text-indigo-700 font-medium transition-colors">忘记密码？</router-link>
            </div>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400"><i class="fa fa-lock"></i></span>
              <input v-model="pw" type="password" id="password"
                class="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none"
                placeholder="请输入密码" required>
            </div>
          </div>

          <button type="submit"
            class="w-full bg-gradient-to-r from-slate-800 to-indigo-900 hover:from-slate-700 hover:to-indigo-800 text-white py-3.5 rounded-2xl font-medium transition-all duration-300 shadow-lg shadow-indigo-900/10 hover:shadow-indigo-900/20 hover:-translate-y-0.5 text-sm tracking-wide"
            :disabled="ld">
            <span v-if="ld"><i class="fa fa-spinner fa-spin mr-2"></i>登录中...</span>
            <span v-else><i class="fa fa-sign-in mr-2"></i>登 录</span>
          </button>
        </form>

        <div class="mt-8 text-center text-sm text-slate-500">
          还没有账户？<router-link to="/register" class="text-indigo-600 hover:text-indigo-700 font-semibold transition-colors">立即注册 →</router-link>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useFlashStore } from '../stores/flash'
import api from '../api'

const router = useRouter(); const auth = useAuthStore(); const flash = useFlashStore()
const un = ref(''); const pw = ref(''); const err = ref(''); const ld = ref(false)

async function go() {
  if (!un.value || !pw.value) { err.value = '用户名和密码不能为空'; return }
  ld.value = true; err.value = ''
  try {
    const r = await api.post('/api/login', { username: un.value, password: pw.value })
    if (r.data.code === 200) { auth.login(r.data.data.token, r.data.data.username, r.data.data.user_id); flash.show('登录成功！', 'success'); router.push('/search') }
    else err.value = r.data.message
  } catch (e) { err.value = e.response?.data?.message || '网络错误' } finally { ld.value = false }
}
</script>
