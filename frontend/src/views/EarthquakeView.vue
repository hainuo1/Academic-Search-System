<template>
<div class="min-h-screen bg-slate-50">

  <div class="bg-gradient-to-r from-slate-800 via-indigo-900 to-blue-950 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      <h1 class="text-3xl font-bold flex items-center gap-3">
        <i class="fa fa-warning text-amber-400"></i>地震监测分析
      </h1>
      <p class="text-slate-300 mt-2 ml-1">
        全球地震数据 · 震级深度分析 · AI 科学解读
      </p>
    </div>
  </div>

  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">

    <!-- 筛选栏 -->
    <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-sm border border-slate-100 p-5 mb-6">
      <div class="flex flex-wrap items-end gap-3">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-xs text-slate-500 font-medium mb-1.5">地点搜索</label>
          <input v-model="filters.keyword" placeholder="输入地点名称..."
            class="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 outline-none transition-all"
            @keyup.enter="searchQuakes" />
        </div>
        <div class="w-[140px]">
          <label class="block text-xs text-slate-500 font-medium mb-1.5">年份</label>
          <select v-model="filters.year"
            class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm bg-white focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 outline-none transition-all">
            <option value="">全部年份</option>
            <option v-for="y in availableYears" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <div class="w-[140px]">
          <label class="block text-xs text-slate-500 font-medium mb-1.5">最低震级</label>
          <select v-model="filters.minMag"
            class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm bg-white focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 outline-none transition-all">
            <option value="">不限</option>
            <option value="5">≥ M5.0（有感地震）</option>
            <option value="6">≥ M6.0（强震）</option>
            <option value="7">≥ M7.0（大地震）</option>
          </select>
        </div>
        <div class="flex gap-2">
          <button @click="searchQuakes"
            class="px-6 py-2.5 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-xl text-sm font-medium hover:shadow-lg hover:shadow-indigo-900/20 transition-all flex items-center gap-2">
            <i class="fa fa-search text-xs"></i>搜索
          </button>
          <button @click="resetFilters"
            class="px-4 py-2.5 bg-slate-100 text-slate-600 rounded-xl text-sm font-medium hover:bg-slate-200 transition-all">
            <i class="fa fa-refresh"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- 加载 -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-slate-500 mt-3 text-sm">加载地震数据中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="quakes.length === 0" class="text-center py-16">
      <div class="text-5xl text-slate-300 mb-4"><i class="fa fa-map-o"></i></div>
      <p class="text-slate-500">暂未找到符合条件的地震数据</p>
      <p class="text-slate-400 text-sm mt-1">请调整筛选条件或等待数据导入</p>
    </div>

    <!-- 卡片列表 -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <div v-for="q in quakes" :key="q.event_id"
        @click="goDetail(q.event_id)"
        class="group bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-amber-200 transition-all duration-300 cursor-pointer p-5 transform hover:-translate-y-1">

        <div class="flex items-start justify-between mb-3">
          <div class="flex-1 min-w-0">
            <h3 class="text-base font-bold text-slate-800 truncate group-hover:text-amber-600 transition-colors">
              {{ q.place }}
            </h3>
            <p class="text-xs text-slate-400 mt-0.5">{{ q.datetime }}</p>
          </div>
          <span :class="magBadgeClass(q.magnitude)"
            class="px-3 py-1.5 rounded-full text-sm font-bold whitespace-nowrap ml-2">
            M{{ q.magnitude.toFixed(1) }}
          </span>
        </div>

        <div class="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-100">
          <div class="text-center">
            <div class="text-lg font-bold text-slate-700">{{ q.depth }}</div>
            <div class="text-[10px] text-slate-400">震源深度(km)</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold text-slate-700">{{ q.mag_type || '-' }}</div>
            <div class="text-[10px] text-slate-400">震级类型</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold text-slate-700">{{ q.nst || '-' }}</div>
            <div class="text-[10px] text-slate-400">台站数</div>
          </div>
        </div>

        <div class="mt-3 pt-3 border-t border-slate-100 flex justify-end">
          <span class="text-indigo-600 text-sm font-medium group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
            查看详情 <i class="fa fa-arrow-right text-xs"></i>
          </span>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-2 pb-8">
      <button @click="goPage(page - 1)" :disabled="page <= 1"
        class="px-4 py-2 rounded-xl text-sm font-medium border border-slate-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-all">
        <i class="fa fa-chevron-left mr-1"></i>上一页
      </button>
      <span class="px-4 py-2 text-sm text-slate-500">
        第 {{ page }} / {{ totalPages }} 页（共 {{ totalCount }} 条地震事件）
      </span>
      <button @click="goPage(page + 1)" :disabled="page >= totalPages"
        class="px-4 py-2 rounded-xl text-sm font-medium border border-slate-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-all">
        下一页<i class="fa fa-chevron-right ml-1"></i>
      </button>
    </div>

  </div>
</div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()

const quakes = ref([])
const availableYears = ref([])
const totalCount = ref(0)
const page = ref(1)
const totalPages = ref(1)
const loading = ref(false)

const filters = reactive({ keyword: '', year: '', minMag: '' })

function magBadgeClass(m) {
  if (m >= 7) return 'bg-red-100 text-red-700'
  if (m >= 6) return 'bg-orange-100 text-orange-700'
  if (m >= 5) return 'bg-amber-100 text-amber-700'
  return 'bg-blue-100 text-blue-700'
}

async function fetchQuakes() {
  loading.value = true
  try {
    const params = { page: page.value }
    if (filters.year) params.year = filters.year
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.minMag) params.min_mag = filters.minMag

    const { data: res } = await api.get('/api/earthquake/list', { params })
    if (res.code === 200) {
      quakes.value = res.data.earthquakes
      totalCount.value = res.data.total_count
      totalPages.value = res.data.total_pages
      availableYears.value = res.data.available_years
    }
  } catch (e) {
    console.error('获取地震数据失败:', e)
  } finally {
    loading.value = false
  }
}

function searchQuakes() { page.value = 1; fetchQuakes() }
function resetFilters() { filters.keyword = ''; filters.year = ''; filters.minMag = ''; page.value = 1; fetchQuakes() }
function goPage(p) { if (p < 1 || p > totalPages.value) return; page.value = p; fetchQuakes(); window.scrollTo({ top: 0, behavior: 'smooth' }) }
function goDetail(id) { router.push(`/earthquake/${id}`) }

onMounted(() => { fetchQuakes(); window.scrollTo({ top: 0, behavior: 'instant' }); })
</script>
