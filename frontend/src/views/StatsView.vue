<template>
<div class="max-w-7xl mx-auto px-4 py-10">
  <div class="mb-10">
    <div class="flex items-center gap-3">
      <div class="w-10 h-10 bg-gradient-to-br from-slate-800 to-indigo-900 rounded-xl flex items-center justify-center shadow-md">
        <i class="fa fa-bar-chart text-white text-base"></i>
      </div>
      <div>
        <h1 class="text-2xl font-bold text-slate-800">系统数据统计</h1>
        <p class="text-slate-500 text-sm">查看系统热门关键词、活跃用户、高被引文献等统计数据</p>
      </div>
    </div>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

    <!-- 1. 热门关键词 -->
    <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-6 hover:shadow-lg transition-all">
      <h2 class="text-sm font-bold text-slate-700 mb-5 flex items-center gap-2 pb-3 border-b border-slate-100">
        <div class="w-8 h-8 bg-orange-50 rounded-lg flex items-center justify-center"><i class="fa fa-fire text-orange-500 text-sm"></i></div>热门关键词
      </h2>
      <div class="space-y-2.5">
        <div v-for="(item, i) in s.keyword_rank" :key="i" class="flex justify-between items-center py-2">
          <span class="text-sm text-slate-700 font-medium">{{ i + 1 }}. {{ item.keyword }}</span>
          <span class="bg-orange-50 text-orange-600 px-2.5 py-0.5 rounded-lg text-xs font-medium">{{ item.count }} 次</span>
        </div>
        <p v-if="!s.keyword_rank?.length" class="text-slate-400 text-center py-6 text-sm">暂无数据</p>
      </div>
    </div>

    <!-- 2. 活跃用户 -->
    <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-6 hover:shadow-lg transition-all">
      <h2 class="text-sm font-bold text-slate-700 mb-5 flex items-center gap-2 pb-3 border-b border-slate-100">
        <div class="w-8 h-8 bg-emerald-50 rounded-lg flex items-center justify-center"><i class="fa fa-users text-emerald-500 text-sm"></i></div>活跃用户
      </h2>
      <div class="space-y-2.5">
        <div v-for="(item, i) in s.user_rank" :key="i" class="flex justify-between items-center py-2">
          <span class="text-sm text-slate-700 font-medium">{{ i + 1 }}. {{ item.username }}</span>
          <span class="bg-emerald-50 text-emerald-600 px-2.5 py-0.5 rounded-lg text-xs font-medium">{{ item.count }} 次</span>
        </div>
        <p v-if="!s.user_rank?.length" class="text-slate-400 text-center py-6 text-sm">暂无数据</p>
      </div>
    </div>

    <!-- 3. 高被引 -->
    <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-6 hover:shadow-lg transition-all">
      <h2 class="text-sm font-bold text-slate-700 mb-5 flex items-center gap-2 pb-3 border-b border-slate-100">
        <div class="w-8 h-8 bg-amber-50 rounded-lg flex items-center justify-center"><i class="fa fa-trophy text-amber-500 text-sm"></i></div>高被引文献
      </h2>
      <div class="space-y-2.5">
        <div v-for="(item, i) in s.citation_rank" :key="i" class="flex justify-between items-center py-2">
          <router-link :to="`/document/${item.id}`" class="text-sm text-slate-700 hover:text-indigo-600 transition-colors truncate flex-1 mr-2 font-medium">{{ i + 1 }}. {{ item.title }}</router-link>
          <span class="bg-amber-50 text-amber-600 px-2.5 py-0.5 rounded-lg text-xs font-medium whitespace-nowrap">{{ item.count }} 次</span>
        </div>
        <p v-if="!s.citation_rank?.length" class="text-slate-400 text-center py-6 text-sm">暂无数据</p>
      </div>
    </div>

    <!-- 4. 浏览排行 -->
    <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-6 hover:shadow-lg transition-all">
      <h2 class="text-sm font-bold text-slate-700 mb-5 flex items-center gap-2 pb-3 border-b border-slate-100">
        <div class="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center"><i class="fa fa-eye text-blue-500 text-sm"></i></div>按浏览次数
      </h2>
      <div class="space-y-2.5">
        <div v-for="(item, i) in s.view_rank" :key="i" class="flex justify-between items-center py-2">
          <router-link :to="`/document/${item.id}`" class="text-sm text-slate-700 hover:text-indigo-600 transition-colors truncate flex-1 mr-2 font-medium">{{ i + 1 }}. {{ item.title }}</router-link>
          <span class="bg-blue-50 text-blue-600 px-2.5 py-0.5 rounded-lg text-xs font-medium whitespace-nowrap">{{ item.view_count }} 次</span>
        </div>
        <p v-if="!s.view_rank?.length" class="text-slate-400 text-center py-6 text-sm">暂无数据</p>
      </div>
    </div>

    <!-- 5. 下载排行 -->
    <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-6 hover:shadow-lg transition-all">
      <h2 class="text-sm font-bold text-slate-700 mb-5 flex items-center gap-2 pb-3 border-b border-slate-100">
        <div class="w-8 h-8 bg-emerald-50 rounded-lg flex items-center justify-center"><i class="fa fa-download text-emerald-500 text-sm"></i></div>按下载次数
      </h2>
      <div class="space-y-2.5">
        <div v-for="(item, i) in s.download_rank" :key="i" class="flex justify-between items-center py-2">
          <router-link :to="`/document/${item.id}`" class="text-sm text-slate-700 hover:text-indigo-600 transition-colors truncate flex-1 mr-2 font-medium">{{ i + 1 }}. {{ item.title }}</router-link>
          <span class="bg-emerald-50 text-emerald-600 px-2.5 py-0.5 rounded-lg text-xs font-medium whitespace-nowrap">{{ item.download_count }} 次</span>
        </div>
        <p v-if="!s.download_rank?.length" class="text-slate-400 text-center py-6 text-sm">暂无数据</p>
      </div>
    </div>

    <!-- 6. 收藏排行 -->
    <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-6 hover:shadow-lg transition-all">
      <h2 class="text-sm font-bold text-slate-700 mb-5 flex items-center gap-2 pb-3 border-b border-slate-100">
        <div class="w-8 h-8 bg-red-50 rounded-lg flex items-center justify-center"><i class="fa fa-heart text-red-500 text-sm"></i></div>按收藏次数
      </h2>
      <div class="space-y-2.5">
        <div v-for="(item, i) in s.favorite_rank" :key="i" class="flex justify-between items-center py-2">
          <router-link :to="`/document/${item.id}`" class="text-sm text-slate-700 hover:text-indigo-600 transition-colors truncate flex-1 mr-2 font-medium">{{ i + 1 }}. {{ item.title }}</router-link>
          <span class="bg-red-50 text-red-500 px-2.5 py-0.5 rounded-lg text-xs font-medium whitespace-nowrap"><i class="fa fa-heart mr-0.5"></i>{{ item.count }}</span>
        </div>
        <p v-if="!s.favorite_rank?.length" class="text-slate-400 text-center py-6 text-sm">暂无数据</p>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
const s = ref({ keyword_rank:[], user_rank:[], citation_rank:[], view_rank:[], download_rank:[], favorite_rank:[] })
onMounted(async () => { try { const r = await api.get('/api/stats'); if (r.data.code === 200) s.value = r.data.data } catch (e) { console.error('加载统计数据失败:', e) } })
</script>
