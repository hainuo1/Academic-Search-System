<template>
<div class="min-h-screen bg-slate-50">

  <!-- 页面标题栏 -->
  <div class="bg-gradient-to-r from-slate-800 via-indigo-900 to-blue-950 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-8">
      <h1 class="text-3xl font-bold flex items-center gap-3">
        <i class="fa fa-cloud text-cyan-400"></i>龙卷风监测分析
      </h1>
      <p class="text-slate-300 mt-2 ml-1">
        美国历史龙卷风数据 · EF等级分析 · AI 科学解读
        <span class="ml-4 inline-flex items-center gap-1.5 px-3 py-0.5 bg-white/10 rounded-full text-xs text-blue-200/80 border border-white/10">
          <i class="fa fa-map-marker"></i>数据范围：美国全境（NOAA SPC 1950-2024）
        </span>
      </p>
    </div>
  </div>

  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">

    <!-- 筛选栏 -->
    <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-sm border border-slate-100 p-5 mb-6">
      <div class="flex flex-wrap items-end gap-3">
        <div class="flex-1 min-w-[200px]">
          <label class="block text-xs text-slate-500 font-medium mb-1.5">地点搜索</label>
          <input v-model="filters.keyword" placeholder="输入州名或城市，如 Oklahoma..."
            class="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 outline-none transition-all"
            @keyup.enter="searchTornadoes" />
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
          <label class="block text-xs text-slate-500 font-medium mb-1.5">最低EF等级</label>
          <select v-model="filters.minEF"
            class="w-full px-3 py-2.5 border border-slate-200 rounded-xl text-sm bg-white focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 outline-none transition-all">
            <option value="">不限</option>
            <option value="1">≥ EF1（弱）</option>
            <option value="2">≥ EF2（强）</option>
            <option value="3">≥ EF3（剧烈）</option>
            <option value="4">≥ EF4（毁灭）</option>
          </select>
        </div>
        <div class="flex gap-2">
          <button @click="searchTornadoes"
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
      <p class="text-slate-500 mt-3 text-sm">加载龙卷风数据中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="tornadoes.length === 0" class="text-center py-16">
      <div class="text-5xl text-slate-300 mb-4"><i class="fa fa-cloud"></i></div>
      <p class="text-slate-500">暂未找到符合条件的龙卷风数据</p>
      <p class="text-slate-400 text-sm mt-1">请尝试调整筛选条件或等待数据导入</p>
    </div>

    <!-- 龙卷风卡片列表 -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <div v-for="t in tornadoes" :key="t.event_id"
        @click="goDetail(t.event_id)"
        class="group bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm hover:shadow-xl hover:border-cyan-200 transition-all duration-300 cursor-pointer p-5 transform hover:-translate-y-1">

        <!-- 卡片头部 -->
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1 min-w-0">
            <h3 class="text-base font-bold text-slate-800 truncate group-hover:text-cyan-600 transition-colors">
              {{ buildTornadoTitle(t) }}
            </h3>
            <p class="text-xs text-slate-400 mt-0.5">{{ t.datetime }}</p>
          </div>
          <span :class="efBadgeClass(t.ef_scale)"
            class="px-3 py-1 rounded-full text-sm font-bold whitespace-nowrap ml-2">
            {{ formatEFLabel(t.ef_scale) }}
          </span>
        </div>

        <!-- 关键数据 -->
        <div class="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-100">
          <div class="text-center">
            <div class="text-lg font-bold text-red-600">{{ t.deaths != null ? t.deaths : '-' }}</div>
            <div class="text-[10px] text-slate-400">死亡</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold text-amber-600">{{ t.injuries != null ? t.injuries : '-' }}</div>
            <div class="text-[10px] text-slate-400">受伤</div>
          </div>
          <div class="text-center">
            <div class="text-lg font-bold text-slate-700">{{ t.casualties != null ? t.casualties : '-' }}</div>
            <div class="text-[10px] text-slate-400">总伤亡</div>
          </div>
        </div>

        <!-- 查看详情 -->
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
        第 {{ page }} / {{ totalPages }} 页（共 {{ totalCount }} 条龙卷风事件）
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

const tornadoes = ref([])
const availableYears = ref([])
const totalCount = ref(0)
const page = ref(1)
const totalPages = ref(1)
const loading = ref(false)

const filters = reactive({
  keyword: '',
  year: '',
  minEF: '',
})

// 构建卡片标题："OH, FIPS0" 格式（州缩写, 县级FIPS代码）
// place 字段存的是 stn(FIPS)，province 存的是州缩写
function buildTornadoTitle(t) {
  var province = (t.province || '').trim();
  var place = (t.place || '').trim();
  if (province && place) return province + ', FIPS' + place;
  if (province) return province;
  if (place) return 'FIPS' + place;
  return 'N/A';
}

function formatEFLabel(ef) {
  var s = String(ef || '').trim();
  if (!s) return 'N/A';
  // 如果已经是标准 EF0~EF5 格式
  if (/^EF[0-5]$/i.test(s)) return s.toUpperCase();
  // 如果是 F0~F5 格式
  if (/^F[0-5]$/i.test(s)) return 'E' + s.toUpperCase();
  // 纯数字 0~5
  if (/^[0-5]$/.test(s)) return 'EF' + s;
  return s;
}

function efBadgeClass(ef) {
  var s = String(ef || '').trim();
  if (!s) return 'bg-gray-100 text-gray-600';
  var m = parseInt(s.replace(/^EF/i, '').replace(/^F/i, ''), 10);
  if (isNaN(m) || m < 0) return 'bg-gray-100 text-gray-600';
  if (m >= 4) return 'bg-red-100 text-red-700'
  if (m >= 3) return 'bg-orange-100 text-orange-700'
  if (m >= 2) return 'bg-amber-100 text-amber-700'
  if (m >= 1) return 'bg-blue-100 text-blue-700'
  return 'bg-gray-100 text-gray-600'
}

async function fetchTornadoes() {
  loading.value = true
  try {
    const params = { page: page.value }
    if (filters.year) params.year = filters.year
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.minEF) params.min_ef = filters.minEF

    const { data: res } = await api.get('/api/tornado/list', { params })
    if (res.code === 200) {
      tornadoes.value = res.data.tornadoes || []
      totalCount.value = res.data.total_count || 0
      totalPages.value = res.data.total_pages || 1
      availableYears.value = res.data.available_years || []
    }
  } catch (e) {
    console.error('获取龙卷风数据失败:', e)
  } finally {
    loading.value = false
  }
}

function searchTornadoes() {
  page.value = 1
  fetchTornadoes()
}

function resetFilters() {
  filters.keyword = ''
  filters.year = ''
  filters.minEF = ''
  page.value = 1
  fetchTornadoes()
}

function goPage(p) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  fetchTornadoes()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function goDetail(id) {
  router.push(`/tornado/${id}`)
}

onMounted(() => {
  fetchTornadoes()
  window.scrollTo({ top: 0, behavior: 'instant' })
})
</script>
