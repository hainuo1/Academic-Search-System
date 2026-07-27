<template>
<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-blue-950 to-indigo-950 py-8 px-4 relative overflow-hidden">
  <div class="absolute inset-0 opacity-15" style="background-image:radial-gradient(1px 1px at 10% 20%,#38bdf8,transparent),radial-gradient(1px 1px at 80% 30%,#818cf8,transparent),radial-gradient(1px 1px at 40% 70%,#22d3ee,transparent),radial-gradient(1px 1px at 70% 80%,#e2e8f0,transparent)"></div>
  <div class="absolute top-0 left-1/4 w-[400px] h-[250px] bg-cyan-500/8 rounded-full blur-[120px]"></div>
  <div class="absolute bottom-0 right-1/4 w-[350px] h-[200px] bg-indigo-500/8 rounded-full blur-[120px]"></div>
  <div class="w-full max-w-4xl bg-white/5 backdrop-blur-2xl rounded-3xl overflow-hidden flex flex-col md:flex-row border border-white/8 shadow-2xl shadow-black/20 relative z-10">
    <div class="w-full md:w-2/5 p-8 md:p-10 flex flex-col justify-between relative overflow-hidden">
      <div class="absolute -top-20 -right-20 w-60 h-60 bg-cyan-500/15 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-20 -left-20 w-60 h-60 bg-indigo-500/10 rounded-full blur-3xl"></div>
      <div class="relative z-10"><div class="flex items-center gap-2 text-white/60 mb-10"><i class="fa fa-cloud text-cyan-400/80 text-lg"></i><span class="text-sm font-light tracking-widest">气象科学研究数据平台 v6.0</span></div><h2 class="text-3xl font-light text-white leading-tight tracking-wide">加入我们</h2><p class="text-blue-200/50 text-sm mt-3 leading-relaxed max-w-xs">注册后即可访问自然灾害观测数据分析服务、使用 AI 科学解读引擎，并检索学术文献资源。</p></div>
      <div class="relative z-10 mt-8 space-y-2"><div class="flex items-center gap-3 text-white/30 text-xs"><div class="w-1.5 h-1.5 rounded-full bg-cyan-400/60"></div><span>热带气旋路径可视化与科学解读</span></div><div class="flex items-center gap-3 text-white/30 text-xs"><div class="w-1.5 h-1.5 rounded-full bg-indigo-400/60"></div><span>学术文献多维度检索与管理</span></div><div class="flex items-center gap-3 text-white/30 text-xs"><div class="w-1.5 h-1.5 rounded-full bg-blue-400/60"></div><span>注册后即可免费使用全部功能</span></div></div>
    </div>
    <div class="w-full md:w-3/5 p-8 md:p-10 flex items-center justify-center bg-white/[0.03] backdrop-blur-sm">
      <div class="w-full max-w-sm">
        <div class="md:hidden text-center mb-6"><h2 class="text-2xl font-light text-white">创建账户</h2><p class="text-blue-200/50 text-sm mt-1">填写信息，即刻开始</p></div>
        <div v-if="err" class="mb-5 bg-red-500/10 border border-red-500/20 text-red-300 px-4 py-3 rounded-2xl flex items-center text-sm backdrop-blur-sm"><i class="fa fa-exclamation-circle mr-2.5 flex-shrink-0"></i><span>{{ err }}</span></div>
        <form @submit.prevent="go" class="space-y-3">
          <div><label class="block text-xs font-medium text-slate-400 mb-1.5 tracking-wide">用户名</label><input v-model="un" type="text" class="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" placeholder="2-20个字符" required></div>
          <div><label class="block text-xs font-medium text-slate-400 mb-1.5 tracking-wide">邮箱</label><input v-model="em" type="email" class="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" placeholder="请输入您的邮箱地址" required></div>
          <div><label class="block text-xs font-medium text-slate-400 mb-1.5 tracking-wide">密码</label><input v-model="pw" type="password" class="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" placeholder="8-50个字符，不含空格" required></div>
          <div><label class="block text-xs font-medium text-slate-400 mb-1.5 tracking-wide">确认密码</label><input v-model="cp" type="password" class="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" placeholder="请再次输入密码" required></div>
          <div class="border-t border-white/5 pt-4 mt-2"><p class="text-xs font-medium text-slate-400 mb-3 tracking-wide">安全问题（用于找回密码）</p>
            <div class="space-y-2.5"><div><label class="block text-[11px] font-medium text-slate-500 mb-1">问题 1</label><input v-model="q1" type="text" class="w-full px-3.5 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" placeholder="例如：您母亲的姓名是？" required></div>
            <div><label class="block text-[11px] font-medium text-slate-500 mb-1">答案 1</label><input v-model="a1" type="text" class="w-full px-3.5 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" placeholder="请输入答案" required></div>
            <div><label class="block text-[11px] font-medium text-slate-500 mb-1">问题 2</label><input v-model="q2" type="text" class="w-full px-3.5 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" placeholder="例如：您的小学名称是？" required></div>
            <div><label class="block text-[11px] font-medium text-slate-500 mb-1">答案 2</label><input v-model="a2" type="text" class="w-full px-3.5 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-slate-500 focus:bg-white/8 focus:border-cyan-500/50 focus:ring-0 transition-all outline-none" placeholder="请输入答案" required></div></div>
          </div>
          <button type="submit" class="w-full bg-white/10 hover:bg-white/15 text-white/90 py-3.5 rounded-2xl font-medium transition-all duration-300 border border-white/10 hover:border-white/20 text-sm tracking-wide mt-3" :disabled="ld"><span v-if="ld"><i class="fa fa-spinner fa-spin mr-2"></i>注册中...</span><span v-else>注 册</span></button>
        </form>
        <div class="mt-7 text-center text-sm text-slate-500">已有账户？<router-link to="/login" class="text-cyan-400/80 hover:text-cyan-300 font-medium transition-colors ml-1">立即登录</router-link></div>
      </div>
    </div>
  </div>
</div>
</template>
<script setup>
import { ref } from 'vue'; import { useRouter } from 'vue-router'; import { useFlashStore } from '../stores/flash'; import api from '../api'
const router=useRouter(),flash=useFlashStore(),un=ref(''),em=ref(''),pw=ref(''),cp=ref(''),q1=ref(''),a1=ref(''),q2=ref(''),a2=ref(''),err=ref(''),ld=ref(false)
async function go(){err.value=''; if(pw.value!==cp.value){err.value='两次输入的密码不一致';return} if(pw.value.length<8){err.value='密码至少需要8个字符';return} if(pw.value.includes(' ')){err.value='密码不能包含空格';return}; ld.value=true;try{const r=await api.post('/api/register',{username:un.value,email:em.value,password:pw.value,confirm_password:cp.value,question1:q1.value,answer1:a1.value,question2:q2.value,answer2:a2.value});if(r.data.code===200){flash.show('注册成功，请登录','success');router.push('/login')}else err.value=r.data.message}catch(e){err.value=e.response?.data?.message||'网络错误'}finally{ld.value=false}}
</script>