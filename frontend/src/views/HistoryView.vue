<template>
<main class="max-w-4xl mx-auto px-4 py-8">
  <div class="mb-8">
    <div class="flex items-center mb-2">
      <div class="w-10 h-10 bg-gradient-to-br from-slate-800 to-indigo-900 rounded-xl flex items-center justify-center mr-3 shadow-md">
        <i class="fa fa-history text-white text-lg"></i>
      </div>
      <div>
        <h1 class="text-2xl font-bold text-slate-800">我的历史</h1>
        <p class="text-slate-500 text-sm">查看您的检索历史和浏览记录</p>
      </div>
    </div>
  </div>

  <!-- 检索历史 -->
  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 mb-6 overflow-hidden">
    <div @click="showSearch = !showSearch" class="flex items-center justify-between px-6 py-4 cursor-pointer hover:bg-slate-50 transition-colors">
      <div class="flex items-center gap-3">
        <i class="fa fa-search text-indigo-500 text-base"></i>
        <span class="text-base font-semibold text-slate-700">检索历史</span>
        <span class="text-sm text-slate-400 ml-1">（共 {{ sTotal }} 条记录）</span>
      </div>
      <i :class="showSearch ? 'fa fa-chevron-up' : 'fa fa-chevron-down'" class="text-slate-400 transition-transform duration-200"></i>
    </div>
    <div v-show="showSearch" class="px-6 pb-6">
      <div v-if="sh.length" class="space-y-2">
        <div v-for="(h, i) in sh" :key="i" class="flex flex-col md:flex-row md:items-center justify-between gap-3 px-4 py-4 rounded-2xl border border-slate-100 hover:border-indigo-200 hover:shadow-lg transition-all duration-200 bg-white">
          <div class="flex items-center">
            <div class="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center mr-4"><i class="fa fa-search text-indigo-500"></i></div>
            <div>
              <a href="#" @click.prevent="reSearch(h.keyword)" class="text-base font-semibold text-indigo-600 hover:text-indigo-800 transition-colors">{{ h.keyword }}</a>
              <p class="text-xs text-slate-400 mt-0.5">点击关键词可快速重新搜索</p>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <span class="flex items-center text-slate-500 text-sm"><i class="fa fa-clock-o mr-1.5"></i>{{ h.time }}</span>
            <a href="#" @click.prevent="reSearch(h.keyword)" class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all text-sm font-medium"><i class="fa fa-redo mr-1.5"></i>重新搜索</a>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-10">
        <div class="w-20 h-20 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-full flex items-center justify-center mx-auto mb-4"><i class="fa fa-search text-indigo-400 text-3xl"></i></div>
        <p class="text-slate-500 text-sm">暂无检索历史</p>
        <router-link to="/search" class="text-indigo-600 hover:text-indigo-800 text-sm mt-2 inline-block font-medium">去检索文献</router-link>
      </div>
      <div v-if="sps > 1" class="mt-4 flex justify-center gap-1.5"><button v-for="p in sPageList" :key="p" @click="load('search', p)" :class="p === sp ? 'bg-gradient-to-r from-slate-800 to-indigo-900 text-white border-transparent shadow-lg' : 'bg-white border-slate-200 hover:bg-slate-50 text-slate-600'" class="px-4 py-2 rounded-xl text-sm border transition-all shadow-sm font-medium min-w-[44px]">{{ p }}</button></div>
    </div>
  </div>

  <!-- 浏览历史 -->
  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 mb-6 overflow-hidden">
    <div @click="showBrowse = !showBrowse" class="flex items-center justify-between px-6 py-4 cursor-pointer hover:bg-slate-50 transition-colors">
      <div class="flex items-center gap-3">
        <i class="fa fa-eye text-emerald-500 text-base"></i>
        <span class="text-base font-semibold text-slate-700">浏览历史</span>
        <span class="text-sm text-slate-400 ml-1">（共 {{ bTotal }} 条记录）</span>
      </div>
      <i :class="showBrowse ? 'fa fa-chevron-up' : 'fa fa-chevron-down'" class="text-slate-400 transition-transform duration-200"></i>
    </div>
    <div v-show="showBrowse" class="px-6 pb-6">
      <div v-if="bh.length" class="space-y-2">
        <div v-for="(h, i) in bh" :key="i" class="flex flex-col md:flex-row md:items-center justify-between gap-3 px-4 py-4 rounded-2xl border border-slate-100 hover:border-emerald-200 hover:shadow-lg transition-all duration-200 bg-white">
          <div class="flex items-center">
            <div class="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center mr-4"><i class="fa fa-file-text-o text-emerald-500"></i></div>
            <div>
              <router-link :to="`/document/${h.document_id}`" class="text-base font-semibold text-indigo-600 hover:text-indigo-800 transition-colors">{{ h.title }}</router-link>
              <p class="text-xs text-slate-400 mt-0.5">作者：{{ h.author }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <span class="flex items-center text-slate-500 text-sm"><i class="fa fa-clock-o mr-1.5"></i>{{ h.view_time }}</span>
            <router-link :to="`/document/${h.document_id}`" class="inline-flex items-center px-4 py-2 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all text-sm font-medium"><i class="fa fa-eye mr-1.5"></i>查看详情</router-link>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-10">
        <div class="w-20 h-20 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-full flex items-center justify-center mx-auto mb-4"><i class="fa fa-eye text-indigo-400 text-3xl"></i></div>
        <p class="text-slate-500 text-sm">暂无浏览历史</p>
        <router-link to="/search" class="text-indigo-600 hover:text-indigo-800 text-sm mt-2 inline-block font-medium">去浏览文献</router-link>
      </div>
      <div v-if="bps > 1" class="mt-4 flex justify-center gap-1.5"><button v-for="p in bPageList" :key="p" @click="load('browse', p)" :class="p === bp ? 'bg-gradient-to-r from-slate-800 to-indigo-900 text-white border-transparent shadow-lg' : 'bg-white border-slate-200 hover:bg-slate-50 text-slate-600'" class="px-4 py-2 rounded-xl text-sm border transition-all shadow-sm font-medium min-w-[44px]">{{ p }}</button></div>
    </div>
  </div>

  <!-- 小提示卡片 -->
  <div class="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-2xl p-6 border border-indigo-100 shadow-sm">
    <div class="flex items-start">
      <div class="w-10 h-10 bg-white/80 backdrop-blur-xl rounded-xl flex items-center justify-center mr-4 shadow-sm"><i class="fa fa-lightbulb-o text-indigo-500"></i></div>
      <div><h4 class="font-semibold text-slate-800 mb-1 text-sm">小提示</h4><p class="text-slate-600 text-sm">检索历史保存您的每一次搜索，点击"重新搜索"可快速执行相同检索（保留最近100条）。浏览历史记录您看过的每一篇文献，方便随时回溯。</p></div>
    </div>
  </div>
</main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
const router = useRouter()
const sh = ref([]); const bh = ref([]); const sp = ref(1); const bp = ref(1); const sps = ref(1); const bps = ref(1)
const sTotal = ref(0); const bTotal = ref(0); const showSearch = ref(false); const showBrowse = ref(false)
// 窗口化分页：只显示当前页附近的页码（最多5个），避免页码过多溢出
const sPageList = computed(() => windowPages(sp.value, sps.value))
const bPageList = computed(() => windowPages(bp.value, bps.value))
function windowPages(cur, total) {
  const a = []
  let start = Math.max(1, cur - 2)
  let end = Math.min(total, cur + 2)
  if (end - start < 4) {
    if (start === 1) end = Math.min(total, 5)
    else start = Math.max(1, end - 4)
  }
  for (let i = start; i <= end; i++) a.push(i)
  return a
}
async function load(type, p) { try { const params = {}; if (type === 'search') params.search_page = p; else params.browse_page = p; const r = await api.get('/api/history', { params }); if (r.data.code === 200) { sh.value = r.data.data.search_histories; bh.value = r.data.data.browse_histories; sp.value = r.data.data.search_page; bp.value = r.data.data.browse_page; sps.value = r.data.data.search_pages; bps.value = r.data.data.browse_pages; sTotal.value = r.data.data.search_total; bTotal.value = r.data.data.browse_total } } catch (e) { console.error('加载历史记录失败:', e) } }
function reSearch(kw) { router.push({ path: '/search', query: { keyword: kw } }) }
onMounted(() => load('search', 1))
</script>
