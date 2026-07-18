<template>
<div class="bg-gradient-to-br from-slate-950 via-blue-950 to-indigo-950 min-h-screen flex items-center justify-center py-12 px-4 relative overflow-hidden">
  <div class="absolute inset-0 opacity-10"
    style="background-image:radial-gradient(1px 1px at 20% 30%,#38bdf8,transparent),radial-gradient(1px 1px at 70% 60%,#818cf8,transparent)">
  </div>
  <div class="absolute top-1/3 left-1/4 w-60 h-60 bg-cyan-500/8 rounded-full blur-[100px]"></div>

  <div class="max-w-md w-full bg-white/5 backdrop-blur-2xl rounded-2xl shadow-2xl overflow-hidden border border-white/8 relative z-10">

    <div class="p-8 text-center relative overflow-hidden">
      <div class="absolute -top-10 -right-10 w-32 h-32 bg-cyan-500/10 rounded-full blur-xl"></div>
      <div class="absolute -bottom-8 -left-8 w-24 h-24 bg-indigo-500/10 rounded-full blur-xl"></div>
      <div class="relative z-10">
        <div class="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-4 backdrop-blur-sm border border-white/10">
          <i class="fa fa-key text-2xl text-cyan-400/80"></i>
        </div>
        <h2 class="text-2xl font-light text-white tracking-wide">找回密码</h2>
        <p class="text-blue-200/40 text-sm mt-2">回答安全问题验证身份</p>
      </div>
    </div>

    <div class="p-8 pt-0">
      <div v-if="err" class="bg-red-500/10 border border-red-500/20 text-red-300 px-4 py-3 rounded-xl mb-5 flex items-center text-sm backdrop-blur-sm">
        <i class="fa fa-exclamation-circle mr-2.5 flex-shrink-0"></i><span>{{ err }}</span>
      </div>
      <div v-if="ok" class="bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 px-4 py-3 rounded-xl mb-5 flex items-center text-sm backdrop-blur-sm">
        <i class="fa fa-check-circle mr-2.5 flex-shrink-0"></i><span>{{ ok }}</span>
      </div>

      <form @submit.prevent="step === 1 ? goStep1() : goStep2()" class="space-y-5">
        <div>
          <label class="block text-xs font-medium text-slate-400 mb-2 tracking-wide">用户名</label>
          <input v-model="un" type="text" :disabled="step === 2"
            class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-2xl text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none disabled:opacity-40 disabled:cursor-not-allowed"
            placeholder="请输入您的用户名" required>
        </div>

        <div v-if="step === 1">
          <label class="block text-xs font-medium text-slate-400 mb-2 tracking-wide">验证码</label>
          <div class="flex items-center gap-3">
            <input v-model="cap" type="text" class="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-2xl text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" placeholder="请输入图片中的字符" required maxlength="4" autocomplete="off">
            <img :src="capUrl" @click="refreshCap" class="h-11 w-auto border border-white/10 rounded-xl cursor-pointer hover:border-cyan-500/50 transition-colors" alt="验证码" title="点击刷新">
          </div>
          <p class="text-slate-500 text-xs mt-2">点击图片刷新验证码</p>
        </div>

        <button v-if="step === 1" type="submit"
          class="w-full bg-white/10 hover:bg-white/15 text-white/90 py-3.5 rounded-2xl font-medium transition-all duration-300 border border-white/10 text-sm tracking-wide" :disabled="ld">
          <span v-if="ld"><i class="fa fa-spinner fa-spin mr-2"></i>验证中...</span>
          <span v-else>获取安全问题</span>
        </button>

        <template v-if="step === 2">
          <div class="space-y-4">
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-2 tracking-wide">安全问题一</label>
              <p class="text-white/80 text-sm mb-2">{{ q1 }}</p>
              <input v-model="a1" type="text" placeholder="请输入答案" class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-2xl text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" required>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-2 tracking-wide">安全问题二</label>
              <p class="text-white/80 text-sm mb-2">{{ q2 }}</p>
              <input v-model="a2" type="text" placeholder="请输入答案" class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-2xl text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" required>
            </div>
          </div>

          <div class="border-t border-white/5 pt-5 mt-2 space-y-4">
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-2 tracking-wide">新密码</label>
              <input v-model="np" type="password" class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-2xl text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" placeholder="8-50个字符" required>
            </div>
            <div>
              <label class="block text-xs font-medium text-slate-400 mb-2 tracking-wide">确认新密码</label>
              <input v-model="cp" type="password" class="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-2xl text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" placeholder="请再次输入" required>
            </div>
          </div>

          <button type="submit"
            class="w-full bg-white/10 hover:bg-white/15 text-white/90 py-3.5 rounded-2xl font-medium transition-all duration-300 border border-white/10 text-sm tracking-wide" :disabled="ld">
            <span v-if="ld"><i class="fa fa-spinner fa-spin mr-2"></i>重置中...</span>
            <span v-else>验证并重置密码</span>
          </button>
        </template>
      </form>

      <div class="mt-7 text-center text-sm text-slate-500">
        已想起密码？<router-link to="/login" class="text-cyan-400/80 hover:text-cyan-300 font-medium transition-colors ml-1">返回登录</router-link>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'

const step = ref(1)
const un = ref('')
const cap = ref('')
const capUrl = ref(`http://localhost:5000/api/captcha?t=${Date.now()}`)
const q1 = ref('')
const q2 = ref('')
const a1 = ref('')
const a2 = ref('')
const np = ref('')
const cp = ref('')
const err = ref('')
const ok = ref('')
const ld = ref(false)

function refreshCap() { capUrl.value = `http://localhost:5000/api/captcha?t=${Date.now()}` }

async function goStep1() {
  err.value = ''
  ld.value = true
  try {
    const r = await api.post('/api/forgot_password', {
      username: un.value, captcha: cap.value, step: '1',
    })
    if (r.data.code === 200) {
      q1.value = r.data.data.questions[0]
      q2.value = r.data.data.questions[1]
      step.value = 2
    } else {
      err.value = r.data.message
      refreshCap()
    }
  } catch (e) {
    err.value = e.response?.data?.message || '网络错误'
    refreshCap()
  } finally {
    ld.value = false
  }
}

async function goStep2() {
  err.value = ''
  ld.value = true
  try {
    const r = await api.post('/api/forgot_password', {
      username: un.value, step: '2',
      answer1: a1.value, answer2: a2.value,
      new_password: np.value, confirm_password: cp.value,
    })
    if (r.data.code === 200) {
      ok.value = r.data.message
      err.value = ''
    } else {
      err.value = r.data.message
    }
  } catch (e) {
    err.value = e.response?.data?.message || '网络错误'
  } finally {
    ld.value = false
  }
}
</script>
