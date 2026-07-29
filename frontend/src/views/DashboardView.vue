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

    <!-- ========== 模块一：热带气旋 ========== -->
    <div class="mb-10">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-9 h-9 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center shadow-md shadow-cyan-500/20">
          <i class="fa fa-dot-circle-o text-white text-base"></i>
        </div>
        <div>
          <h2 class="text-xl font-bold text-slate-700">热带气旋观测分析</h2>
          <p class="text-xs text-slate-400 mt-0.5">西北太平洋 · 路径可视化 · AI 科学解读</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <!-- 主导航卡片 -->
        <router-link to="/typhoon"
          class="lg:col-span-2 group block bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-cyan-200 transition-all duration-300 transform hover:-translate-y-1 overflow-hidden">
          <div class="h-44 bg-gradient-to-br from-slate-800 via-indigo-900 to-blue-950 flex items-center justify-center relative overflow-hidden">
            <div class="absolute inset-0 opacity-20" style="background:radial-gradient(circle at 30% 40%,#22d3ee 0%,transparent 50%),radial-gradient(circle at 70% 60%,#818cf8 0%,transparent 50%)"></div>
            <div class="relative flex flex-col items-center">
              <div class="w-24 h-24 rounded-full border-4 border-cyan-400/40 flex items-center justify-center relative mb-2 shadow-[0_0_40px_rgba(34,211,238,0.3)]">
                <div class="absolute inset-0 rounded-full border-2 border-cyan-300/60 animate-spin" style="animation-duration:8s"></div>
                <div class="absolute inset-2 rounded-full border border-cyan-200/40 animate-spin" style="animation-duration:5s;animation-direction:reverse"></div>
                <div class="w-8 h-8 bg-cyan-400/80 rounded-full shadow-[0_0_20px_rgba(34,211,238,0.6)]"></div>
              </div>
              <span class="text-white/90 text-sm font-medium">进入热带气旋分析 →</span>
            </div>
          </div>
          <div class="p-5 flex items-center justify-between">
            <div>
              <h3 class="text-lg font-bold text-slate-700 group-hover:text-cyan-600 transition-colors">热带气旋完整数据</h3>
              <p class="text-sm text-slate-400 mt-1">最佳路径集 · 强度演变 · 登陆分析</p>
            </div>
            <i class="fa fa-chevron-right text-slate-300 group-hover:text-cyan-500 transition-colors"></i>
          </div>
        </router-link>

        <!-- 功能入口（不可点击，仅作展示） -->
        <div class="flex flex-col gap-3">
          <div
            class="group bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex items-center gap-4 transition-all duration-300">
            <div class="w-11 h-11 bg-gradient-to-br from-cyan-100 to-blue-100 rounded-xl flex items-center justify-center shrink-0">
              <i class="fa fa-map text-cyan-600 text-lg"></i>
            </div>
            <div>
              <h4 class="text-sm font-semibold text-slate-700">路径可视化</h4>
              <p class="text-xs text-slate-400">交互地图 · 轨迹回放</p>
            </div>
          </div>
          <div
            class="group bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex items-center gap-4 transition-all duration-300">
            <div class="w-11 h-11 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-xl flex items-center justify-center shrink-0">
              <i class="fa fa-magic text-blue-600 text-lg"></i>
            </div>
            <div>
              <h4 class="text-sm font-semibold text-slate-700">AI 智能解读</h4>
              <p class="text-xs text-slate-400">强度分析 · 路径预测</p>
            </div>
          </div>
          <div
            class="group bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex items-center gap-4 transition-all duration-300">
            <div class="w-11 h-11 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-xl flex items-center justify-center shrink-0">
              <i class="fa fa-bar-chart text-indigo-600 text-lg"></i>
            </div>
            <div>
              <h4 class="text-sm font-semibold text-slate-700">统计分析</h4>
              <p class="text-xs text-slate-400">频次 · 强度 · 趋势</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== 模块二：龙卷风 ========== -->
    <div class="mb-10">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-9 h-9 bg-gradient-to-br from-teal-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-md shadow-teal-500/20">
          <i class="fa fa-cloud text-white text-base"></i>
        </div>
        <div>
          <h2 class="text-xl font-bold text-slate-700">龙卷风观测分析</h2>
          <p class="text-xs text-slate-400 mt-0.5">美国全境 · EF等级分析 · 地理分布可视化</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <!-- 主导航卡片 -->
        <router-link to="/tornado"
          class="lg:col-span-2 group block bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-teal-200 transition-all duration-300 transform hover:-translate-y-1 overflow-hidden">
          <div class="h-44 bg-gradient-to-br from-slate-800 via-teal-900 to-emerald-950 flex items-center justify-center relative overflow-hidden">
            <div class="absolute inset-0 opacity-20" style="background:radial-gradient(circle at 40% 40%,#2dd4bf 0%,transparent 50%),radial-gradient(circle at 60% 55%,#34d399 0%,transparent 50%)"></div>
            <div class="relative flex flex-col items-center">
              <i class="fa fa-cloud text-6xl text-teal-400/60 mb-2"></i>
              <span class="text-white/90 text-sm font-medium">进入龙卷风分析 →</span>
            </div>
          </div>
          <div class="p-5 flex items-center justify-between">
            <div>
              <h3 class="text-lg font-bold text-slate-700 group-hover:text-teal-600 transition-colors">龙卷风完整数据</h3>
              <p class="text-sm text-slate-400 mt-1">历史事件 · EF 评级 · 损失评估</p>
            </div>
            <i class="fa fa-chevron-right text-slate-300 group-hover:text-teal-500 transition-colors"></i>
          </div>
        </router-link>

        <!-- 功能入口（不可点击，仅作展示） -->
        <div class="flex flex-col gap-3">
          <div
            class="group bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex items-center gap-4 transition-all duration-300">
            <div class="w-11 h-11 bg-gradient-to-br from-teal-100 to-emerald-100 rounded-xl flex items-center justify-center shrink-0">
              <i class="fa fa-list-ol text-teal-600 text-lg"></i>
            </div>
            <div>
              <h4 class="text-sm font-semibold text-slate-700">EF 等级分析</h4>
              <p class="text-xs text-slate-400">强度分级 · 频次统计</p>
            </div>
          </div>
          <div
            class="group bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex items-center gap-4 transition-all duration-300">
            <div class="w-11 h-11 bg-gradient-to-br from-emerald-100 to-green-100 rounded-xl flex items-center justify-center shrink-0">
              <i class="fa fa-map-marker text-emerald-600 text-lg"></i>
            </div>
            <div>
              <h4 class="text-sm font-semibold text-slate-700">地理分布</h4>
              <p class="text-xs text-slate-400">空间密度 · 热点区域</p>
            </div>
          </div>
          <div
            class="group bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex items-center gap-4 transition-all duration-300">
            <div class="w-11 h-11 bg-gradient-to-br from-green-100 to-lime-100 rounded-xl flex items-center justify-center shrink-0">
              <i class="fa fa-magic text-green-600 text-lg"></i>
            </div>
            <div>
              <h4 class="text-sm font-semibold text-slate-700">AI 科学解读</h4>
              <p class="text-xs text-slate-400">成因分析 · 趋势研判</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== 模块三：地震监测 ========== -->
    <div class="mb-10">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-9 h-9 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center shadow-md shadow-amber-500/20">
          <i class="fa fa-warning text-white text-base"></i>
        </div>
        <div>
          <h2 class="text-xl font-bold text-slate-700">地震监测分析</h2>
          <p class="text-xs text-slate-400 mt-0.5">全球范围 · 震级深度 · PostGIS 空间分析</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <!-- 主导航卡片 -->
        <router-link to="/earthquake"
          class="lg:col-span-2 group block bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-amber-200 transition-all duration-300 transform hover:-translate-y-1 overflow-hidden">
          <div class="h-44 bg-gradient-to-br from-amber-900 via-orange-800 to-red-900 flex items-center justify-center relative overflow-hidden">
            <div class="absolute inset-0 opacity-20" style="background:radial-gradient(circle at 50% 50%,#fbbf24 0%,transparent 70%)"></div>
            <div class="relative flex flex-col items-center">
              <div class="w-20 h-20 flex items-center justify-center relative mb-1">
                <i class="fa fa-warning text-6xl text-amber-400/60"></i>
              </div>
              <span class="text-white/90 text-sm font-medium">进入地震监测 →</span>
            </div>
          </div>
          <div class="p-5 flex items-center justify-between">
            <div>
              <h3 class="text-lg font-bold text-slate-700 group-hover:text-amber-600 transition-colors">地震完整数据</h3>
              <p class="text-sm text-slate-400 mt-1">全球事件 · 多维检索 · AI 评估</p>
            </div>
            <i class="fa fa-chevron-right text-slate-300 group-hover:text-amber-500 transition-colors"></i>
          </div>
        </router-link>

        <!-- 功能入口（不可点击，仅作展示） -->
        <div class="flex flex-col gap-3">
          <div
            class="group bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex items-center gap-4 transition-all duration-300">
            <div class="w-11 h-11 bg-gradient-to-br from-amber-100 to-orange-100 rounded-xl flex items-center justify-center shrink-0">
              <i class="fa fa-globe text-amber-600 text-lg"></i>
            </div>
            <div>
              <h4 class="text-sm font-semibold text-slate-700">空间密度分析</h4>
              <p class="text-xs text-slate-400">PostGIS · 邻近事件</p>
            </div>
          </div>
          <div
            class="group bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex items-center gap-4 transition-all duration-300">
            <div class="w-11 h-11 bg-gradient-to-br from-orange-100 to-red-100 rounded-xl flex items-center justify-center shrink-0">
              <i class="fa fa-line-chart text-orange-600 text-lg"></i>
            </div>
            <div>
              <h4 class="text-sm font-semibold text-slate-700">活动趋势</h4>
              <p class="text-xs text-slate-400">时间序列 · 区域对比</p>
            </div>
          </div>
          <div
            class="group bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex items-center gap-4 transition-all duration-300">
            <div class="w-11 h-11 bg-gradient-to-br from-red-100 to-rose-100 rounded-xl flex items-center justify-center shrink-0">
              <i class="fa fa-magic text-red-600 text-lg"></i>
            </div>
            <div>
              <h4 class="text-sm font-semibold text-slate-700">AI 风险评估</h4>
              <p class="text-xs text-slate-400">DeepSeek · 科学解读</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== 模块四：学术文献检索与管理 ========== -->
    <div class="mt-10">
      <div class="flex items-center gap-3 mb-5">
        <div class="w-9 h-9 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-md shadow-indigo-500/20">
          <i class="fa fa-book text-white text-base"></i>
        </div>
        <div>
          <h2 class="text-xl font-bold text-slate-700">学术文献检索与管理</h2>
          <p class="text-xs text-slate-400 mt-0.5">多维度检索 · 文献管理 · 知识发现</p>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
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
