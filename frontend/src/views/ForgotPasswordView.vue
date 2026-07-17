<template>
<div class="bg-gradient-to-br from-slate-100 via-blue-50 to-indigo-50 min-h-screen flex items-center justify-center py-12 px-4">
  <div class="max-w-md w-full bg-white/80 backdrop-blur-xl rounded-2xl shadow-2xl overflow-hidden border border-white/50">

    <div class="bg-gradient-to-br from-slate-800 to-indigo-900 text-white p-8 text-center relative overflow-hidden">
      <div class="absolute -top-10 -right-10 w-32 h-32 bg-white/5 rounded-full blur-xl"></div>
      <div class="absolute -bottom-8 -left-8 w-24 h-24 bg-white/5 rounded-full blur-xl"></div>
      <div class="relative z-10">
        <div class="w-16 h-16 bg-white/10 rounded-2xl flex items-center justify-center mx-auto mb-4 backdrop-blur-sm">
          <i class="fa fa-key text-2xl text-white"></i>
        </div>
        <h2 class="text-2xl font-bold">找回密码</h2>
        <p class="text-indigo-200/80 text-sm mt-2">回答安全问题验证身份</p>
      </div>
    </div>

    <div class="p-8">
      <div v-if="err" class="bg-red-50 border border-red-100 text-red-600 px-4 py-3 rounded-xl mb-5 flex items-center text-sm backdrop-blur-sm">
        <i class="fa fa-exclamation-circle mr-2.5 flex-shrink-0"></i><span>{{ err }}</span>
      </div>
      <div v-if="ok" class="bg-emerald-50 border border-emerald-100 text-emerald-600 px-4 py-3 rounded-xl mb-5 flex items-center text-sm backdrop-blur-sm">
        <i class="fa fa-check-circle mr-2.5 flex-shrink-0"></i><span>{{ ok }}</span>
      </div>

      <form @submit.prevent="step === 1 ? goStep1() : goStep2()" class="space-y-5">
        <div>
          <label class="block text-sm font-medium text-slate-600 mb-2">用户名</label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400"><i class="fa fa-user-o"></i></span>
            <input v-model="un" type="text" :disabled="step === 2"
              class="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none disabled:opacity-60 disabled:cursor-not-allowed"
              placeholder="请输入您的用户名" required>
          </div>
        </div>

        <!-- 第一步：验证码 -->
        <div v-if="step === 1">
          <label class="block text-sm font-medium text-slate-600 mb-2">验证码 <span class="text-red-400">*</span></label>
          <div class="flex items-center gap-3">
            <input v-model="cap" type="text" class="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="请输入图片中的字符" required maxlength="4" autocomplete="off">
            <img :src="capUrl" @click="refreshCap" class="h-11 w-auto border border-slate-200 rounded-xl cursor-pointer hover:border-indigo-300 transition-colors shadow-sm" alt="验证码" title="点击刷新验证码">
          </div>
          <p class="text-slate-400 text-xs mt-2">点击图片可刷新验证码</p>
        </div>

        <!-- 第一步按钮 -->
        <button v-if="step === 1" type="submit"
          class="w-full bg-gradient-to-r from-slate-800 to-indigo-900 text-white py-3.5 rounded-2xl font-medium hover:from-slate-700 hover:to-indigo-800 transition-all duration-300 shadow-lg shadow-indigo-900/10 hover:shadow-indigo-900/20 hover:-translate-y-0.5 text-sm tracking-wide" :disabled="ld">
          <span v-if="ld"><i class="fa fa-spinner fa-spin mr-2"></i>验证中...</span>
          <span v-else>获取安全问题</span>
        </button>

        <!-- 第二步：安全问题 + 新密码 -->
        <template v-if="step === 2">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2"><i class="fa fa-question-circle text-indigo-500 mr-1.5"></i>{{ qs[0] }}</label>
              <input v-model="a1" type="text" placeholder="请输入答案" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" required>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2"><i class="fa fa-question-circle text-indigo-500 mr-1.5"></i>{{ qs[1] }}</label>
              <input v-model="a2" type="text" placeholder="请输入答案" class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" required>
            </div>
          </div>

          <div class="border-t border-slate-100 pt-5 mt-2 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2">新密码</label>
              <div class="relative">
                <span class="absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400"><i class="fa fa-lock"></i></span>
                <input v-model="np" type="password" class="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="8-50个字符，不含空格" required>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-2">确认新密码</label>
              <div class="relative">
                <span class="absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400"><i class="fa fa-lock"></i></span>
                <input v-model="cp" type="password" class="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-sm text-slate-800 placeholder-slate-400 focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none" placeholder="请再次输入新密码" required>
              </div>
            </div>
          </div>

          <button type="submit"
            class="w-full bg-gradient-to-r from-slate-800 to-indigo-900 text-white py-3.5 rounded-2xl font-medium hover:from-slate-700 hover:to-indigo-800 transition-all duration-300 shadow-lg shadow-indigo-900/10 hover:shadow-indigo-900/20 hover:-translate-y-0.5 text-sm tracking-wide" :disabled="ld">
            <span v-if="ld"><i class="fa fa-spinner fa-spin mr-2"></i>重置中...</span>
            <span v-else>验证并重置密码</span>
          </button>
        </template>
      </form>

      <div class="mt-7 text-center text-sm text-slate-500">
        已想起密码？<router-link to="/login" class="text-indigo-600 hover:text-indigo-700 font-semibold transition-colors">返回登录</router-link>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'

const step = ref(1); const un = ref(''); const cap = ref('')
const capUrl = ref('http://localhost:5000/api/captcha')
const qs = ref([]); const a1 = ref(''); const a2 = ref(''); const np = ref(''); const cp = ref('')
const err = ref(''); const ok = ref(''); const ld = ref(false)

function refreshCap() { capUrl.value = `http://localhost:5000/api/captcha?t=${Date.now()}` }

async function goStep1() {
  err.value = ''; ld.value = true
  try {
    const r = await api.post('/api/forgot_password', { username: un.value, captcha: cap.value, step: '1' })
    if (r.data.code === 200) { qs.value = r.data.data.questions; step.value = 2 }
    else { err.value = r.data.message; refreshCap() }
  } catch (e) { err.value = e.response?.data?.message || '网络错误'; refreshCap() } finally { ld.value = false }
}

async function goStep2() {
  err.value = ''; ld.value = true
  try {
    const r = await api.post('/api/forgot_password', { username: un.value, step: '2', answer1: a1.value, answer2: a2.value, new_password: np.value, confirm_password: cp.value })
    if (r.data.code === 200) { ok.value = r.data.message; err.value = '' }
    else err.value = r.data.message
  } catch (e) { err.value = e.response?.data?.message || '网络错误' } finally { ld.value = false }
}
</script>
