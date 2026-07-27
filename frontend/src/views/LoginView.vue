<template>
<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-blue-950 to-indigo-950 py-12 px-4 relative overflow-hidden">
  <div class="absolute inset-0 opacity-15" style="background-image:radial-gradient(1px 1px at 10% 20%,#38bdf8,transparent),radial-gradient(1px 1px at 80% 30%,#818cf8,transparent),radial-gradient(1px 1px at 40% 70%,#22d3ee,transparent),radial-gradient(1px 1px at 70% 80%,#e2e8f0,transparent),radial-gradient(1px 1px at 20% 90%,#38bdf8,transparent)"></div>
  <div class="absolute top-0 left-1/4 w-[400px] h-[250px] bg-cyan-500/8 rounded-full blur-[120px]"></div>
  <div class="absolute bottom-0 right-1/4 w-[350px] h-[200px] bg-indigo-500/8 rounded-full blur-[120px]"></div>
  <div class="w-full max-w-4xl bg-white/5 backdrop-blur-2xl rounded-3xl overflow-hidden flex flex-col md:flex-row border border-white/8 shadow-2xl shadow-black/20 relative z-10">
    <div class="w-full md:w-2/5 p-8 md:p-10 flex flex-col justify-between relative overflow-hidden">
      <div class="absolute -top-20 -right-20 w-60 h-60 bg-cyan-500/15 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-20 -left-20 w-60 h-60 bg-indigo-500/10 rounded-full blur-3xl"></div>
      <div class="relative z-10"><div class="flex items-center gap-2 text-white/60 mb-10"><i class="fa fa-cloud text-cyan-400/80 text-lg"></i><span class="text-sm font-light tracking-widest">气象科学研究数据平台 v6.0</span></div><h2 class="text-3xl font-light text-white leading-tight tracking-wide">欢迎回来</h2><p class="text-blue-200/50 text-sm mt-3 leading-relaxed max-w-xs">登录您的账户，访问自然灾害观测数据分析与学术文献检索管理服务。</p></div>
      <div class="relative z-10 mt-8 space-y-2"><div class="flex items-center gap-3 text-white/30 text-xs"><div class="w-1.5 h-1.5 rounded-full bg-cyan-400/60"></div><span>热带气旋路径可视化与 AI 科学解读</span></div><div class="flex items-center gap-3 text-white/30 text-xs"><div class="w-1.5 h-1.5 rounded-full bg-indigo-400/60"></div><span>学术文献多维度检索与知识管理</span></div><div class="flex items-center gap-3 text-white/30 text-xs"><div class="w-1.5 h-1.5 rounded-full bg-blue-400/60"></div><span>DeepSeek 大语言模型科学辅助分析</span></div></div>
    </div>
    <div class="w-full md:w-3/5 p-8 md:p-14 flex items-center justify-center bg-white/[0.03] backdrop-blur-sm">
      <div class="w-full max-w-sm">
        <div class="md:hidden text-center mb-8"><h2 class="text-2xl font-light text-white">登录</h2><p class="text-blue-200/50 text-sm mt-1">登录您的账户</p></div>
        <div v-if="err" class="mb-6 bg-red-500/10 border border-red-500/20 text-red-300 px-4 py-3 rounded-2xl flex items-center text-sm backdrop-blur-sm"><i class="fa fa-exclamation-circle mr-2.5 flex-shrink-0"></i><span>{{ err }}</span></div>
        <form @submit.prevent="go" class="space-y-5">
          <div><label class="block text-xs font-medium text-slate-400 mb-2 tracking-wide" for="username">用户名</label><div class="relative"><span class="absolute inset-y-0 left-0 flex items-center pl-4 text-slate-500"><i class="fa fa-user-o"></i></span><input v-model="un" type="text" id="username" class="w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-2xl text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" placeholder="请输入用户名" required></div></div>
          <div><div class="flex justify-between items-center mb-2"><label class="block text-xs font-medium text-slate-400 tracking-wide" for="password">密码</label><router-link to="/forgot_password" class="text-xs text-cyan-400/60 hover:text-cyan-300 transition-colors">忘记密码？</router-link></div><div class="relative"><span class="absolute inset-y-0 left-0 flex items-center pl-4 text-slate-500"><i class="fa fa-lock"></i></span><input v-model="pw" type="password" id="password" class="w-full pl-11 pr-4 py-3 bg-white/5 border border-white/10 rounded-2xl text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" placeholder="请输入密码" required></div></div>
          <button type="submit" class="w-full bg-white/10 hover:bg-white/15 text-white/90 py-3.5 rounded-2xl font-medium transition-all duration-300 border border-white/10 hover:border-white/20 text-sm tracking-wide" :disabled="ld"><span v-if="ld"><i class="fa fa-spinner fa-spin mr-2"></i>登录中...</span><span v-else>登 录</span></button>
        </form>
        <div class="mt-8 text-center text-sm text-slate-500">还没有账户？<router-link to="/register" class="text-cyan-400/80 hover:text-cyan-300 font-medium transition-colors ml-1">立即注册</router-link></div>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref } from 'vue'; import { useRouter } from 'vue-router'; import { useAuthStore } from '../stores/auth'; import { useFlashStore } from '../stores/flash'; import api from '../api'
const router=useRouter(),auth=useAuthStore(),flash=useFlashStore(),un=ref(''),pw=ref(''),err=ref(''),ld=ref(false)
async function go(){if(!un.value||!pw.value){err.value='用户名和密码不能为空';return};ld.value=true;err.value='';try{const r=await api.post('/api/login',{username:un.value,password:pw.value});if(r.data.code===200){auth.login(r.data.data.token,r.data.data.username,r.data.data.user_id);flash.show('登录成功！','success');router.push('/dashboard')}else err.value=r.data.message}catch(e){err.value=e.response?.data?.message||'网络错误'}finally{ld.value=false}}
</script>