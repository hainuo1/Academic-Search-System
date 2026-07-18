<template>
<div class="min-h-screen bg-slate-50">

  <!-- 页面标题栏 -->
  <div class="bg-gradient-to-r from-slate-800 to-indigo-900 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      <h1 class="text-3xl font-bold flex items-center gap-3">
        <i class="fa fa-bolt text-yellow-400"></i>热带气旋观测分析
      </h1>
      <p class="text-slate-300 mt-2 ml-1">
        历史路径可视化 · 强度时序分析 · AI 科学解读
        <span class="ml-4 inline-flex items-center gap-1.5 px-3 py-0.5 bg-white/10 rounded-full text-xs text-blue-200/80 border border-white/10">
          <i class="fa fa-globe"></i>数据范围：西北太平洋（100°E–180°E, 0°–60°N）
        </span>
      </p>
    </div>
  </div>

  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">

    <!-- 筛选栏 -->
    <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-sm border border-slate-100 p-5 mb-6">
      <div class="flex flex-wrap items-end gap-3">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-xs text-slate-500 font-medium mb-1.5">台风名称搜索</label>
          <input v-model="filters.keyword" placeholder="输入台风名称，如 HAIYAN..."
            class="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 outline-none transition-all"
            @keyup.enter="searchTyphoons" />
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
          <label class="block text-xs text-slate-500 font-medium mb-1.5">最低风速(kts)</label>
          <select v-model="filters.minWind"
            class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm bg-white focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 outline-none transition-all">
            <option value="">不限</option>
            <option value="34">≥34 (TS+)</option>
            <option value="64">≥64 (TY+)</option>
            <option value="100">≥100 (STY+)</option>
            <option value="130">≥130 (Super TY)</option>
          </select>
        </div>
        <div class="flex gap-2">
          <button @click="searchTyphoons"
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

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
      <p class="text-slate-500 mt-3 text-sm">加载台风数据中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="typhoons.length === 0" class="text-center py-16">
      <div class="text-5xl text-slate-300 mb-4"><i class="fa fa-cloud"></i></div>
      <p class="text-slate-500">暂未找到符合条件的台风数据</p>
      <p class="text-slate-400 text-sm mt-1">请尝试调整筛选条件或等待数据导入</p>
    </div>

    <!-- 台风卡片列表 -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <div v-for="t in typhoons" :key="t.typhoon_id"
        @click="goDetail(t.typhoon_id)"
        class="group bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-indigo-200 transition-all duration-300 cursor-pointer p-5 transform hover:-translate-y-1">

        <!-- 卡片头部 -->
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1 min-w-0">
            <h3 class="text-lg font-bold text-slate-800 truncate group-hover:text-indigo-700 transition-colors">
              {{ t.typhoon_name }}
            </h3>
            <p class="text-xs text-slate-400 mt-0.5">{{ t.typhoon_id }}</p>
          </div>
          <span :class="categoryBadgeClass(t.max_wind)"
            class="px-2.5 py-1 rounded-full text-xs font-semibold whitespace-nowrap ml-2">
            {{ categoryLabel(t.max_wind) }}
          </span>
        </div>

        <!-- 关键数据 -->
        <div class="grid grid-cols-2 gap-3 mb-3">
          <div class="bg-slate-50 rounded-xl p-3 text-center">
            <div class="text-xl font-bold text-slate-800">{{ t.max_wind <= 0 ? '-' : t.max_wind }}</div>
            <div class="text-xs text-slate-400 mt-0.5">最大风速 (kts)</div>
          </div>
          <div class="bg-slate-50 rounded-xl p-3 text-center">
            <div class="text-xl font-bold text-slate-800">{{ t.min_pressure >= 9999 ? '-' : t.min_pressure }}</div>
            <div class="text-xs text-slate-400 mt-0.5">最低气压 (hPa)</div>
          </div>
          <div class="bg-slate-50 rounded-xl p-3 text-center">
            <div class="text-lg font-bold text-slate-800">{{ t.season }}</div>
            <div class="text-xs text-slate-400 mt-0.5">年份</div>
          </div>
          <div class="bg-slate-50 rounded-xl p-3 text-center">
            <div class="text-lg font-bold text-slate-800">{{ t.total_points }}</div>
            <div class="text-xs text-slate-400 mt-0.5">路径点</div>
          </div>
        </div>

        <!-- 时间范围 -->
        <div class="flex items-center gap-2 text-xs text-slate-400">
          <i class="fa fa-clock-o"></i>
          <span>{{ t.start_time }} ~ {{ t.end_time }}</span>
        </div>

        <!-- 查看详情按钮 -->
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
        第 {{ page }} / {{ totalPages }} 页（共 {{ totalCount }} 个台风）
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

const typhoons = ref([])
const availableYears = ref([])
const totalCount = ref(0)
const page = ref(1)
const totalPages = ref(1)
const loading = ref(false)

const filters = reactive({
  keyword: '',
  year: '',
  minWind: '',
})

function categoryLabel(wind) {
  if (wind >= 130) return 'Super TY'
  if (wind >= 100) return 'STY'
  if (wind >= 64) return 'TY'
  if (wind >= 34) return 'TS'
  return 'TD'
}

function categoryBadgeClass(wind) {
  if (wind >= 130) return 'bg-red-100 text-red-700'
  if (wind >= 100) return 'bg-orange-100 text-orange-700'
  if (wind >= 64) return 'bg-amber-100 text-amber-700'
  if (wind >= 34) return 'bg-yellow-100 text-yellow-700'
  return 'bg-blue-100 text-blue-700'
}

async function fetchTyphoons() {
  loading.value = true
  try {
    const params = { page: page.value }
    if (filters.year) params.year = filters.year
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.minWind) params.min_wind = filters.minWind

    const { data: res } = await api.get('/api/typhoon/list', { params })
    if (res.code === 200) {
      typhoons.value = res.data.typhoons
      totalCount.value = res.data.total_count
      totalPages.value = res.data.total_pages
      availableYears.value = res.data.available_years
    }
  } catch (e) {
    console.error('获取台风列表失败:', e)
  } finally {
    loading.value = false
  }
}

function searchTyphoons() {
  page.value = 1
  fetchTyphoons()
}

function resetFilters() {
  filters.keyword = ''
  filters.year = ''
  filters.minWind = ''
  page.value = 1
  fetchTyphoons()
}

function goPage(p) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  fetchTyphoons()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goDetail(id) {
  router.push(`/typhoon/${id}`)
}

onMounted(() => {
  fetchTyphoons()
})
</script>
