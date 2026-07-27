<template>
<div :class="{ 'bg-white': auth.isLoggedIn }">
  <nav v-if="auth.isLoggedIn" class="bg-white/80 backdrop-blur-xl shadow-sm border-b border-slate-100 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <div class="flex items-center">
          <router-link to="/dashboard" class="flex items-center gap-3 group">
            <div class="w-9 h-9 bg-gradient-to-br from-slate-800 to-indigo-900 rounded-xl flex items-center justify-center group-hover:shadow-lg group-hover:shadow-indigo-900/20 transition-all">
              <i class="fa fa-cloud text-white text-sm"></i>
            </div>
            <span class="text-lg font-bold text-slate-800 tracking-tight">气象科学研究数据平台 v6.0</span>
          </router-link>
        </div>
        <div class="hidden md:flex items-center gap-1">
          <router-link to="/dashboard" class="text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-all px-3 py-2 rounded-xl text-sm font-medium flex items-center gap-1.5">
            <i class="fa fa-home text-xs text-slate-400"></i>首页
          </router-link>
          <router-link to="/profile" class="text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition-all px-3 py-2 rounded-xl text-sm font-medium flex items-center gap-1.5">
            <i class="fa fa-user-o text-xs text-slate-400"></i>个人中心
          </router-link>
          <a @click="doLogout" class="text-slate-400 hover:text-red-500 transition-colors px-3 py-2 rounded-xl cursor-pointer text-sm flex items-center gap-1.5">
            <i class="fa fa-sign-out text-xs"></i>退出登录
          </a>
        </div>
      </div>
    </div>
  </nav>

  <div v-if="flash.message && auth.isLoggedIn" class="max-w-7xl mx-auto px-4 pt-4">
    <div :class="flashClass" class="rounded-2xl p-4 flex items-center text-sm backdrop-blur-sm border">
      <i :class="flashIcon" class="mr-3 flex-shrink-0"></i>{{ flash.message }}
    </div>
  </div>

  <main><router-view /></main>

  <footer v-if="auth.isLoggedIn" class="bg-slate-900 text-white py-8 mt-16">
    <div class="max-w-7xl mx-auto px-4 text-center">
      <p class="text-slate-400 mb-1.5">&copy; 2026 南京农业大学 · 气象科学研究数据平台 v6.0</p>
      <p class="text-slate-500 text-sm">丁俊杰 · <a href="mailto:hainuo@stu.njau.edu.cn" class="hover:text-indigo-400 transition-colors">hainuo@stu.njau.edu.cn</a></p>
    </div>
  </footer>
</div>
</template>
<script setup>
import { computed } from 'vue'; import { useRouter } from 'vue-router'; import { useAuthStore } from './stores/auth'; import { useFlashStore } from './stores/flash'
const auth=useAuthStore(),flash=useFlashStore(),router=useRouter()
const flashClass=computed(()=>{const t=flash.type;if(t==='success')return 'bg-emerald-50 border-emerald-100 text-emerald-600';if(t==='warning')return 'bg-amber-50 border-amber-100 text-amber-700';if(t==='error')return 'bg-red-50 border-red-100 text-red-600';return 'bg-blue-50 border-blue-100 text-blue-600'})
const flashIcon=computed(()=>{const t=flash.type;if(t==='success')return 'fa fa-check-circle';if(t==='warning')return 'fa fa-exclamation-triangle';if(t==='error')return 'fa fa-exclamation-circle';return 'fa fa-info-circle'})
function doLogout(){auth.logout();router.push('/welcome');flash.show('已退出登录','success')}
</script>