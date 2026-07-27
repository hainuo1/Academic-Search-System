<template>
<div class="min-h-screen bg-slate-50">

  <div class="bg-gradient-to-r from-slate-800 via-indigo-900 to-blue-950 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      <h1 class="text-2xl font-bold flex items-center gap-3">
        <i class="fa fa-globe text-cyan-300"></i>气象科学研究数据平台
      </h1>
    </div>
  </div>

  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-8">

    <!-- 自然灾害观测数据分析 -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-8 h-8 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center shadow-md shadow-cyan-500/20">
          <i class="fa fa-globe text-white text-sm"></i>
        </div>
        <h2 class="text-xl font-bold text-slate-700">自然灾害观测数据分析</h2>
        <span class="text-xs text-slate-400">基于权威数据集的可视化与智能解读</span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <router-link to="/typhoon"
          class="group block bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-cyan-200 transition-all duration-300 transform hover:-translate-y-1 overflow-hidden">
          <div class="h-36 bg-gradient-to-br from-slate-800 via-indigo-900 to-blue-950 flex items-center justify-center relative overflow-hidden">
            <div class="absolute inset-0 opacity-20" style="background:radial-gradient(circle at 30% 40%,#22d3ee 0%,transparent 50%),radial-gradient(circle at 70% 60%,#818cf8 0%,transparent 50%)"></div>
            <div class="relative flex flex-col items-center">
              <div class="w-20 h-20 rounded-full border-4 border-cyan-400/40 flex items-center justify-center relative mb-1 shadow-[0_0_30px_rgba(34,211,238,0.3)]">
                <div class="absolute inset-0 rounded-full border-2 border-cyan-300/60 animate-spin" style="animation-duration:8s"></div>
                <div class="absolute inset-2 rounded-full border border-cyan-200/40 animate-spin" style="animation-duration:5s;animation-direction:reverse"></div>
                <div class="w-6 h-6 bg-cyan-400/80 rounded-full shadow-[0_0_15px_rgba(34,211,238,0.6)]"></div>
              </div>
            </div>
          </div>
          <div class="p-5">
            <h3 class="text-lg font-bold text-slate-700 group-hover:text-cyan-600 transition-colors">热带气旋</h3>
            <p class="text-sm text-slate-400 mt-1">西北太平洋 · 路径可视化 · AI 解读</p>
          </div>
        </router-link>

        <router-link to="/tornado"
          class="group block bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-cyan-200 transition-all duration-300 transform hover:-translate-y-1 overflow-hidden">
          <div class="h-36 bg-gradient-to-br from-slate-800 via-indigo-900 to-blue-950 flex items-center justify-center relative overflow-hidden">
            <div class="absolute inset-0 opacity-20" style="background:radial-gradient(circle at 40% 40%,#22d3ee 0%,transparent 50%),radial-gradient(circle at 60% 55%,#818cf8 0%,transparent 50%)"></div>
            <div class="relative"><i class="fa fa-cloud text-5xl text-cyan-400/70"></i></div>
          </div>
          <div class="p-5">
            <h3 class="text-lg font-bold text-slate-700 group-hover:text-cyan-600 transition-colors">龙卷风</h3>
            <p class="text-sm text-slate-400 mt-1">美国全境 · EF等级分析 · AI 解读</p>
          </div>
        </router-link>

        <router-link to="/earthquake"
          class="group block bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-amber-200 transition-all duration-300 transform hover:-translate-y-1 overflow-hidden">
          <div class="h-36 bg-gradient-to-br from-amber-900 via-orange-800 to-red-900 flex items-center justify-center relative overflow-hidden">
            <div class="absolute inset-0 opacity-20" style="background:radial-gradient(circle at 50% 50%,#fbbf24 0%,transparent 70%)"></div>
            <div class="relative flex flex-col items-center">
              <div class="w-16 h-16 flex items-center justify-center relative">
                <i class="fa fa-warning text-5xl text-amber-400/70"></i>
              </div>
            </div>
          </div>
          <div class="p-5">
            <h3 class="text-lg font-bold text-slate-700 group-hover:text-amber-600 transition-colors">地震监测</h3>
            <p class="text-sm text-slate-400 mt-1">全球范围 · 震级深度 · AI 评估</p>
          </div>
        </router-link>
      </div>
    </div>

    <!-- 学术文献检索与管理 -->
    <div class="mt-10">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-md shadow-indigo-500/20">
          <i class="fa fa-book text-white text-sm"></i>
        </div>
        <h2 class="text-xl font-bold text-slate-700">学术文献检索与管理</h2>
        <span class="text-xs text-slate-400">多维度检索 · 文献管理 · 知识发现</span>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <router-link to="/search"
          class="group bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-indigo-200 transition-all duration-300 p-5 transform hover:-translate-y-1">
          <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mb-4 shadow-md shadow-blue-500/20 group-hover:scale-110 transition-transform">
            <i class="fa fa-search text-white text-lg"></i>
          </div>
          <h3 class="text-base font-semibold text-slate-700 group-hover:text-indigo-600 transition-colors">文献检索</h3>
          <p class="text-xs text-slate-400 mt-1">标题 · 作者 · 分类 · 关键词 · 全文</p>
        </router-link>

        <router-link to="/upload"
          class="group bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-indigo-200 transition-all duration-300 p-5 transform hover:-translate-y-1">
          <div class="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center mb-4 shadow-md shadow-green-500/20 group-hover:scale-110 transition-transform">
            <i class="fa fa-upload text-white text-lg"></i>
          </div>
          <h3 class="text-base font-semibold text-slate-700 group-hover:text-indigo-600 transition-colors">文献上传</h3>
          <p class="text-xs text-slate-400 mt-1">PDF 上传 · 自动全文提取</p>
        </router-link>

        <router-link to="/my_documents"
          class="group bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-indigo-200 transition-all duration-300 p-5 transform hover:-translate-y-1">
          <div class="w-12 h-12 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center mb-4 shadow-md shadow-amber-500/20 group-hover:scale-110 transition-transform">
            <i class="fa fa-file-text text-white text-lg"></i>
          </div>
          <h3 class="text-base font-semibold text-slate-700 group-hover:text-indigo-600 transition-colors">个人文献库</h3>
          <p class="text-xs text-slate-400 mt-1">文献管理 · 信息编辑</p>
        </router-link>

        <router-link to="/favorites"
          class="group bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-indigo-200 transition-all duration-300 p-5 transform hover:-translate-y-1">
          <div class="w-12 h-12 bg-gradient-to-br from-yellow-400 to-yellow-500 rounded-xl flex items-center justify-center mb-4 shadow-md shadow-yellow-400/20 group-hover:scale-110 transition-transform">
            <i class="fa fa-star text-white text-lg"></i>
          </div>
          <h3 class="text-base font-semibold text-slate-700 group-hover:text-indigo-600 transition-colors">文献收藏</h3>
          <p class="text-xs text-slate-400 mt-1">个人知识库 · 随时查阅</p>
        </router-link>

        <router-link to="/history"
          class="group bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-indigo-200 transition-all duration-300 p-5 transform hover:-translate-y-1">
          <div class="w-12 h-12 bg-gradient-to-br from-gray-600 to-gray-700 rounded-xl flex items-center justify-center mb-4 shadow-md shadow-gray-500/20 group-hover:scale-110 transition-transform">
            <i class="fa fa-history text-white text-lg"></i>
          </div>
          <h3 class="text-base font-semibold text-slate-700 group-hover:text-indigo-600 transition-colors">使用记录</h3>
          <p class="text-xs text-slate-400 mt-1">检索记录 · 浏览记录</p>
        </router-link>

        <router-link to="/stats"
          class="group bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-indigo-200 transition-all duration-300 p-5 transform hover:-translate-y-1">
          <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mb-4 shadow-md shadow-purple-500/20 group-hover:scale-110 transition-transform">
            <i class="fa fa-bar-chart text-white text-lg"></i>
          </div>
          <h3 class="text-base font-semibold text-slate-700 group-hover:text-indigo-600 transition-colors">统计总览</h3>
          <p class="text-xs text-slate-400 mt-1">高频关键词 · 活跃研究者</p>
        </router-link>
      </div>
    </div>

  </div>
</div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
const auth = useAuthStore()
const router = useRouter()
function doLogout() { auth.logout(); router.push('/welcome') }
</script>
