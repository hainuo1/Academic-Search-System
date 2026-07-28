<template>
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

  <!-- ====== 搜索区域 ====== -->
  <div class="bg-gradient-to-br from-slate-800 via-slate-900 to-indigo-950 rounded-3xl shadow-2xl p-8 md:p-10 mb-8 relative overflow-hidden">
    <div class="absolute -top-20 -right-20 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl"></div>
    <div class="absolute -bottom-16 -left-16 w-48 h-48 bg-blue-400/5 rounded-full blur-3xl"></div>
    <div class="relative z-10">
      <div class="flex items-center gap-4 mb-6">
        <div class="w-12 h-12 bg-white/10 rounded-2xl flex items-center justify-center backdrop-blur-sm">
          <i class="fa fa-search text-white text-xl"></i>
        </div>
        <div>
          <h1 class="text-2xl md:text-3xl font-bold text-white tracking-tight">学术文献检索</h1>
          <p class="text-indigo-200/80 text-sm mt-0.5">输入关键词，快速找到您需要的学术文献</p>
        </div>
      </div>

      <div class="flex flex-col sm:flex-row gap-3">
        <div class="flex-1 relative">
          <span class="absolute inset-y-0 left-0 flex items-center pl-5 text-slate-400">
            <i class="fa fa-search text-lg"></i>
          </span>
          <input v-model="keyword" type="text" placeholder="请输入标题、作者或关键词..."
            @keyup.enter="doSearch(1)"
            class="w-full pl-12 pr-4 py-4 bg-white/95 rounded-2xl text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-4 focus:ring-white/20 text-base font-medium shadow-inner">
        </div>
        <div class="sm:w-40">
          <select v-model="searchType"
            class="w-full px-4 py-4 bg-white/95 rounded-2xl text-slate-700 focus:outline-none focus:ring-4 focus:ring-white/20 text-base appearance-none cursor-pointer font-medium">
            <option value="title">📄 标题</option>
            <option value="author">✍️ 作者</option>
            <option value="category">📂 分类</option>
            <option value="keyword">🏷️ 关键词</option>
            <option value="fulltext">📖 全文</option>
          </select>
        </div>
        <button @click="doSearch(1)"
          class="px-10 py-4 bg-white text-slate-800 font-semibold rounded-2xl hover:bg-slate-50 transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2 text-base whitespace-nowrap hover:-translate-y-0.5">
          <i class="fa fa-arrow-right"></i>
          搜索
        </button>
      </div>

      <div v-if="keyword && totalCount >= 0" class="mt-5 text-indigo-200/80 text-sm flex items-center gap-2">
        <i class="fa fa-info-circle"></i>
        共找到 <span class="font-bold text-white text-lg">{{ totalCount }}</span> 条结果
      </div>
    </div>
  </div>

  <!-- ====== 高级筛选 ====== -->
  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 mb-4 overflow-hidden">
    <div @click="showFilter = !showFilter"
      class="flex items-center justify-between px-6 py-4 cursor-pointer hover:bg-slate-50 transition-colors">
      <div class="flex items-center gap-3">
        <i class="fa fa-sliders text-indigo-500 text-base"></i>
        <span class="text-base font-semibold text-slate-700">高级筛选</span>
        <span class="text-sm text-slate-400 ml-1 hidden sm:inline">（可选，用于精确过滤）</span>
      </div>
      <i :class="showFilter ? 'fa fa-chevron-up' : 'fa fa-chevron-down'" class="text-slate-400 transition-transform duration-200"></i>
    </div>
    <div v-show="showFilter" class="px-6 pb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium text-slate-500 mb-1.5"><i class="fa fa-file-text-o mr-1.5"></i>标题包含</label>
          <input v-model="titleFilter" type="text" placeholder="输入标题关键词"
            class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all">
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-500 mb-1.5"><i class="fa fa-user-o mr-1.5"></i>作者包含</label>
          <input v-model="authorFilter" type="text" placeholder="输入作者姓名"
            class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all">
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-500 mb-1.5"><i class="fa fa-folder-o mr-1.5"></i>分类</label>
          <input v-model="categoryFilter" type="text" placeholder="如：人工智能、数据库"
            class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all">
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-slate-500 mb-1.5"><i class="fa fa-tags mr-1.5"></i>关键词</label>
          <input v-model="keywordFilter" type="text" placeholder="输入文献关键词"
            class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all">
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-500 mb-1.5"><i class="fa fa-file-text-o mr-1.5"></i>全文包含</label>
          <input v-model="fulltextFilter" type="text" placeholder="输入PDF内文字"
            class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all">
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-500 mb-1.5"><i class="fa fa-calendar mr-1.5"></i>发布日期</label>
          <div class="flex gap-2">
            <input v-model="startDate" type="date" class="w-1/2 px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all">
            <input v-model="endDate" type="date" class="w-1/2 px-3 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all">
          </div>
        </div>
      </div>
      <div class="flex items-center gap-3 mt-5 pt-4 border-t border-slate-100">
        <button @click="doSearch(1)" class="px-5 py-2.5 bg-gradient-to-r from-slate-800 to-indigo-900 text-white text-sm font-medium rounded-xl transition-all hover:shadow-lg hover:-translate-y-0.5 flex items-center gap-2">
          <i class="fa fa-filter"></i> 应用筛选
        </button>
        <button @click="resetFilters" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 text-sm font-medium rounded-xl transition-all flex items-center gap-2">
          <i class="fa fa-undo"></i> 重置
        </button>
      </div>
    </div>
  </div>

  <!-- ====== 分类浏览 ====== -->
  <div v-if="allCategories.length" class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 mb-8 overflow-hidden">
    <div @click="showCategory = !showCategory"
      class="flex items-center justify-between px-6 py-4 cursor-pointer hover:bg-slate-50 transition-colors">
      <div class="flex items-center gap-3">
        <i class="fa fa-tags text-indigo-500 text-base"></i>
        <span class="text-base font-semibold text-slate-700">按分类浏览</span>
        <span class="text-sm text-slate-400 ml-1 hidden sm:inline">点击标签筛选对应分类的文献</span>
      </div>
      <i :class="showCategory ? 'fa fa-chevron-up' : 'fa fa-chevron-down'" class="text-slate-400 transition-transform duration-200"></i>
    </div>
    <div v-show="showCategory" class="px-6 pb-6">
      <div class="flex flex-wrap gap-2">
        <button @click="selectCategory('')"
          :class="!activeCategory ? 'bg-gradient-to-r from-slate-800 to-indigo-900 text-white shadow-lg' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
          class="px-5 py-2 rounded-full text-sm font-medium transition-all">全部</button>
        <button v-for="cat in allCategories" :key="cat" @click="selectCategory(cat)"
          :class="activeCategory === cat ? 'bg-gradient-to-r from-slate-800 to-indigo-900 text-white shadow-lg' : 'bg-slate-100 text-slate-600 hover:bg-indigo-50 hover:text-indigo-600'"
          class="px-5 py-2 rounded-full text-sm font-medium transition-all">{{ cat }}</button>
      </div>
    </div>
  </div>

  <!-- ====== 搜索结果 ====== -->
  <div v-if="loading" class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-16 text-center">
    <div class="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-6"></div>
    <p class="text-slate-500 text-lg">正在搜索...</p>
  </div>

  <div v-else-if="results.length > 0" class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-6 md:p-8">
    <div class="flex justify-between items-center mb-6 text-sm text-slate-500">
      <span class="text-base">共找到 <strong class="text-slate-800 text-lg">{{ totalCount }}</strong> 条结果</span>
      <span v-if="activeCategory" class="bg-indigo-50 text-indigo-600 px-4 py-1.5 rounded-full text-xs font-medium">分类：{{ activeCategory }}</span>
    </div>

    <div class="space-y-4">
      <div v-for="doc in results" :key="doc.id" class="p-5 border border-slate-100 rounded-2xl hover:shadow-lg hover:border-indigo-200 transition-all duration-200 bg-white group">
        <h3 class="text-lg font-semibold mb-2.5 leading-snug">
          <router-link :to="`/document/${doc.id}`" class="text-slate-800 hover:text-indigo-600 transition-colors" v-html="highlight(doc.title)"></router-link>
        </h3>
        <div class="flex flex-wrap gap-x-6 gap-y-1.5 text-sm text-slate-500 mb-3">
          <span class="flex items-center gap-1.5"><i class="fa fa-user-o w-4 text-center text-slate-400"></i>{{ doc.author }}</span>
          <span class="flex items-center gap-1.5"><i class="fa fa-folder-o w-4 text-center text-slate-400"></i>{{ doc.category }}</span>
          <span class="flex items-center gap-1.5"><i class="fa fa-calendar w-4 text-center text-slate-400"></i>{{ doc.publish_date }}</span>
        </div>
        <div v-if="doc.keywords" class="flex flex-wrap gap-1.5 mb-3.5">
          <span v-for="kw in doc.keywords.split(';')" :key="kw" class="bg-indigo-50 text-indigo-600 px-2.5 py-0.5 rounded-lg text-xs font-medium">{{ kw.trim() }}</span>
        </div>
        <div class="flex gap-5 pt-2 border-t border-slate-50">
          <router-link :to="`/document/${doc.id}`" class="text-sm text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-1.5 transition-colors">
            <i class="fa fa-eye"></i>查看详情
          </router-link>
          <a href="#" @click.prevent="downloadPdf(doc.id)" class="text-sm text-emerald-600 hover:text-emerald-800 font-medium flex items-center gap-1.5 transition-colors">
            <i class="fa fa-download"></i>下载PDF
          </a>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="mt-8 pt-6 border-t border-slate-100">
      <div class="flex justify-center gap-1.5 flex-wrap items-center">
        <button v-if="page > 1" @click="doSearch(page - 1)"
          class="px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm hover:bg-slate-50 transition-all shadow-sm font-medium text-slate-600">← 上一页</button>
        <button v-for="p in visiblePages" :key="p" @click="doSearch(p)"
          :class="p === page ? 'bg-gradient-to-r from-slate-800 to-indigo-900 text-white border-transparent shadow-lg' : 'bg-white border-slate-200 hover:bg-slate-50 text-slate-600'"
          class="px-4 py-2.5 rounded-xl text-sm border transition-all shadow-sm font-medium min-w-[44px]">{{ p }}</button>
        <button v-if="page < totalPages" @click="doSearch(page + 1)"
          class="px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm hover:bg-slate-50 transition-all shadow-sm font-medium text-slate-600">下一页 →</button>
      </div>
    </div>
  </div>

  <div v-else class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-16 text-center">
    <div class="w-28 h-28 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-full flex items-center justify-center mx-auto mb-8">
      <i class="fa fa-search text-indigo-400 text-4xl"></i>
    </div>
    <h3 class="text-2xl font-bold text-slate-700 mb-3">{{ activeCategory ? '该分类下暂无文献' : '开始您的学术探索' }}</h3>
    <p class="text-slate-500 text-base max-w-md mx-auto leading-relaxed">
      <template v-if="activeCategory">分类"{{ activeCategory }}"中还没有文献，您可以上传一篇或尝试其他分类</template>
      <template v-else>在上方搜索框中输入关键词，即可检索海量学术文献</template>
    </p>
    <div v-if="!activeCategory" class="flex flex-wrap justify-center gap-3 mt-6">
      <span class="px-5 py-2.5 bg-slate-100 rounded-xl text-sm text-slate-600 font-medium hover:bg-indigo-50 hover:text-indigo-600 transition-all cursor-pointer">💡 试试搜索 "人工智能"</span>
      <span class="px-5 py-2.5 bg-slate-100 rounded-xl text-sm text-slate-600 font-medium hover:bg-indigo-50 hover:text-indigo-600 transition-all cursor-pointer">💡 试试搜索 "机器学习"</span>
      <span class="px-5 py-2.5 bg-slate-100 rounded-xl text-sm text-slate-600 font-medium hover:bg-indigo-50 hover:text-indigo-600 transition-all cursor-pointer">💡 试试搜索 "深度学习"</span>
    </div>
  </div>

</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '../api'

const keyword = ref('')
const searchType = ref('title')
const titleFilter = ref('')
const authorFilter = ref('')
const categoryFilter = ref('')
const keywordFilter = ref('')
const fulltextFilter = ref('')
const startDate = ref('')
const endDate = ref('')
const showFilter = ref(false)
const showCategory = ref(false)
const activeCategory = ref('')
const results = ref([])
const totalCount = ref(0)
const page = ref(1)
const totalPages = ref(1)
const loading = ref(false)
const allCategories = ref([])

function highlight(text) {
  const kw = keyword.value.trim()
  if (!kw) return text
  const escaped = kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  try {
    return text.replace(new RegExp('(' + escaped + ')', 'gi'), '<span class="search-highlight">$1</span>')
  } catch { return text }
}

const visiblePages = computed(() => {
  const total = totalPages.value
  const cur = page.value
  const pages = []
  let start = Math.max(1, cur - 2)
  let end = Math.min(total, cur + 2)
  if (end - start < 4) {
    if (start === 1) end = Math.min(total, start + 4)
    else start = Math.max(1, end - 4)
  }
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

async function doSearch(p) {
  loading.value = true
  try {
    const params = {}
    if (keyword.value.trim()) { params.keyword = keyword.value.trim(); params.search_type = searchType.value }
    if (titleFilter.value.trim()) params.title = titleFilter.value.trim()
    if (authorFilter.value.trim()) params.author = authorFilter.value.trim()
    if (categoryFilter.value.trim() || activeCategory.value) params.category = categoryFilter.value.trim() || activeCategory.value
    if (keywordFilter.value.trim()) params.keyword_filter = keywordFilter.value.trim()
    if (fulltextFilter.value.trim()) params.fulltext_filter = fulltextFilter.value.trim()
    if (startDate.value) params.start_date = startDate.value
    if (endDate.value) params.end_date = endDate.value
    if (p) params.page = p
    const r = await api.get('/api/search', { params })
    if (r.data.code === 200) {
      const d = r.data.data
      results.value = d.papers || []
      totalCount.value = d.total_count || 0
      page.value = d.page || 1
      totalPages.value = d.total_pages || 1
      allCategories.value = d.all_categories || []
      showCategory.value = !!d.all_categories?.length
    }
  } catch (e) { console.error(e) } finally { loading.value = false }
}

function selectCategory(cat) {
  activeCategory.value = cat
  keyword.value = ''
  doSearch(1)
}

function resetFilters() {
  titleFilter.value = ''; authorFilter.value = ''; categoryFilter.value = ''
  keywordFilter.value = ''; fulltextFilter.value = ''
  startDate.value = ''; endDate.value = ''
  activeCategory.value = ''
  doSearch(1)
}

async function downloadPdf(docId) {
  try {
    const r = await api.get(`/api/download/${docId}`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([r.data]))
    const a = document.createElement('a')
    a.href = url
    const disp = r.headers['content-disposition']
    a.download = disp ? decodeURIComponent(disp.split("filename*=UTF-8''")[1] || disp.split('filename=')[1] || 'document.pdf') : 'document.pdf'
    document.body.appendChild(a); a.click(); document.body.removeChild(a); window.URL.revokeObjectURL(url)
  } catch (e) { console.error('下载失败:', e) }
}

doSearch(1)
</script>
