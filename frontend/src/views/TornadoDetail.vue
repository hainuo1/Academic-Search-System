<template>
<div class="min-h-screen bg-slate-50">

  <div class="bg-gradient-to-r from-slate-800 via-indigo-900 to-blue-950 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">
      <button @click="$router.push('/tornado')"
        class="text-slate-300 hover:text-white transition-colors mb-3 flex items-center gap-1.5 text-sm">
        <i class="fa fa-arrow-left"></i>返回龙卷风列表
      </button>
      <div class="flex items-center gap-3 flex-wrap">
        <h1 class="text-2xl md:text-3xl font-bold">{{ buildTitle() }}</h1>
        <span :class="efBadgeClass(detail.ef_scale)" class="px-3 py-1 rounded-full text-sm font-bold whitespace-nowrap">
          {{ formatEFLabel(detail.ef_scale) }}
        </span>
      </div>
      <p class="text-slate-300 mt-1 text-sm">
        {{ detail.datetime || '未知时间' }} · {{ detail.province || '未知州' }}
      </p>
    </div>
  </div>

  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">

    <!-- 数据概览卡片 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ formatEFLabel(detail.ef_scale) }}</div>
        <div class="text-xs text-slate-500 mt-1">EF 等级</div>
      </div>
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-red-600">{{ detail.deaths != null ? detail.deaths : '-' }}</div>
        <div class="text-xs text-slate-500 mt-1">死亡人数</div>
      </div>
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-amber-600">{{ detail.injuries != null ? detail.injuries : '-' }}</div>
        <div class="text-xs text-slate-500 mt-1">受伤人数</div>
      </div>
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ detail.casualties != null ? detail.casualties : '-' }}</div>
        <div class="text-xs text-slate-500 mt-1">总伤亡</div>
      </div>
    </div>

    <!-- 1. 发生位置地图 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-map-o text-cyan-500"></i>
        <span class="font-semibold text-slate-700">发生位置</span>
        <span class="text-xs text-slate-400 ml-auto">OpenStreetMap · 美国本土</span>
      </div>
      <div class="relative">
        <div id="tornado-map" style="height: 480px;"></div>
        <div v-if="mapLoading" class="absolute inset-0 bg-white/60 flex items-center justify-center z-10">
          <div class="text-center">
            <div class="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p class="text-slate-500 text-sm mt-2">加载地图数据...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. 灾害记录 -->
    <div v-if="detail.damage" class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-file-text-o text-indigo-500"></i>
        <span class="font-semibold text-slate-700">灾害记录</span>
      </div>
      <div class="p-5">
        <p class="text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">{{ detail.damage }}</p>
      </div>
    </div>

    <!-- 2.5 空间密度分析 (PostGIS) -->
    <div v-if="spatialStats" class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-globe text-teal-500"></i>
        <span class="font-semibold text-slate-700">空间密度分析</span>
        <span class="text-xs text-slate-400 ml-auto">PostGIS · {{ spatialStats.radius_km }}km 范围</span>
      </div>
      <div class="p-5">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="text-center bg-slate-50 rounded-xl p-3">
            <div class="text-xl font-bold text-slate-800">{{ spatialStats.nearby_count }}</div>
            <div class="text-xs text-slate-500 mt-1">邻近龙卷风数</div>
          </div>
          <div class="text-center bg-slate-50 rounded-xl p-3">
            <div class="text-xl font-bold text-red-600">{{ spatialStats.total_deaths }}</div>
            <div class="text-xs text-slate-500 mt-1">邻近总死亡人数</div>
          </div>
          <div class="text-center bg-slate-50 rounded-xl p-3">
            <div class="text-xl font-bold text-amber-600">{{ spatialStats.total_injuries }}</div>
            <div class="text-xs text-slate-500 mt-1">邻近总受伤人数</div>
          </div>
          <div class="text-center bg-slate-50 rounded-xl p-3">
            <div class="text-xl font-bold text-slate-800">{{ spatialStats.avg_magnitude }}</div>
            <div class="text-xs text-slate-500 mt-1">邻近平均EF等级</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. EF等级频次分布 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-bar-chart text-amber-500"></i>
        <span class="font-semibold text-slate-700">{{ detail.province || '同州' }} EF 等级频次分布</span>
        <span class="text-xs text-slate-400 ml-auto">含本事件 · NOAA SPC</span>
      </div>
      <div class="p-5">
        <canvas ref="chartCanvas" style="width:100%;height:380px"></canvas>
      </div>
    </div>

    <!-- 4. AI 分析面板 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-magic text-purple-500"></i>
        <span class="font-semibold text-slate-700">AI 科学分析</span>
        <span class="text-xs text-slate-400 ml-auto">基于 DeepSeek 大模型</span>
      </div>
      <div class="p-5">
        <div class="flex flex-wrap gap-2 mb-4">
          <button v-for="opt in analysisTypes" :key="opt.value"
            @click="selectedAnalysis = opt.value; aiResult = ''"
            :class="selectedAnalysis === opt.value
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/20'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
            class="px-4 py-2 rounded-xl text-sm font-medium transition-all">
            <i :class="opt.icon" class="mr-1.5"></i>{{ opt.label }}
          </button>
          <div class="flex-1"></div>
          <button @click="clearCache" :disabled="aiLoading"
            class="px-4 py-2 bg-red-50 border border-red-200 text-red-500 rounded-xl text-sm font-medium hover:bg-red-100 transition-colors disabled:opacity-50 flex items-center gap-1.5">
            <i class="fa fa-trash-o"></i>清理缓存
          </button>
          <button @click="runAIAnalysis"
            :disabled="aiLoading"
            class="px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl text-sm font-medium hover:shadow-lg hover:shadow-purple-600/20 transition-all disabled:opacity-60 flex items-center gap-2">
            <i :class="aiLoading ? 'fa fa-spinner fa-spin' : 'fa fa-play'"></i>
            {{ aiLoading ? 'AI 分析中...' : '开始分析' }}
          </button>
        </div>
        <div v-if="aiResult" class="bg-slate-50 rounded-xl p-5 border border-slate-100">
          <div v-if="aiCached" class="text-center text-xs text-amber-500 font-medium mb-3 bg-amber-50 rounded-lg py-1.5">
            <i class="fa fa-info-circle mr-1"></i>当前回答由缓存生成
          </div>
          <div class="text-slate-700 text-sm whitespace-pre-wrap leading-relaxed">{{ aiResult }}</div>
        </div>
        <div v-else-if="!aiLoading" class="text-center py-8 text-slate-400">
          <i class="fa fa-robot text-3xl mb-2 block"></i>
          <p class="text-sm">选择分析类型，点击"开始分析"获取 AI 解读</p>
        </div>
        <div v-if="aiLoading" class="text-center py-8">
          <div class="inline-flex items-center gap-2 text-indigo-600">
            <div class="w-2 h-2 bg-indigo-600 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-indigo-600 rounded-full animate-bounce delay-150"></div>
            <div class="w-2 h-2 bg-indigo-600 rounded-full animate-bounce delay-300"></div>
          </div>
          <p class="text-slate-500 text-sm mt-3">DeepSeek 正在分析龙卷风数据，请稍候...</p>
        </div>
      </div>
    </div>

  </div>
</div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import api from '../api'

const route = useRoute()
const eventId = route.params.id

const detail = reactive({})
const nearby = ref([])
const mapLoading = ref(true)
const spatialStats = ref(null)

let map = null
let marker = null
let impactCircle = null

function _parseEF(ef) {
  var match = String(ef || '').match(/(\d+)/);
  return match ? parseInt(match[1]) : -1;
}

// 构建详情页标题："OH, FIPS0" 格式
function buildTitle() {
  var prov = (detail.province || '').trim();
  var place = (detail.place || '').trim();
  if (prov && place) return prov + ', FIPS' + place;
  if (prov) return prov;
  if (place) return 'FIPS' + place;
  return '龙卷风事件';
}

function formatEFLabel(ef) {
  var s = String(ef || '').trim();
  if (!s) return 'N/A';
  if (/^EF[0-5]$/i.test(s)) return s.toUpperCase();
  if (/^F[0-5]$/i.test(s)) return 'E' + s.toUpperCase();
  if (/^[0-5]$/.test(s)) return 'EF' + s;
  return s;
}

function efBadgeClass(ef) {
  const m = _parseEF(ef)
  if (m < 0) return 'bg-gray-100 text-gray-600'
  if (m >= 4) return 'bg-red-100 text-red-700'
  if (m >= 3) return 'bg-orange-100 text-orange-700'
  if (m >= 2) return 'bg-amber-100 text-amber-700'
  if (m >= 1) return 'bg-blue-100 text-blue-700'
  return 'bg-gray-100 text-gray-600'
}

function efColor(ef) {
  const m = _parseEF(ef)
  if (m < 0) return '#94a3b8'
  if (m >= 4) return '#ef4444'
  if (m >= 3) return '#f97316'
  if (m >= 2) return '#eab308'
  if (m >= 1) return '#22d3ee'
  return '#94a3b8'
}

// ═══ 地图 — OpenStreetMap ═════════════════════════════
function initMap() {
  if (map) return
  const osmLayer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 18,
  })
  const usBounds = L.latLngBounds([22, -130], [52, -62])
  map = L.map('tornado-map', {
    center: [39.8, -98.5], zoom: 5, minZoom: 3, maxZoom: 18,
    maxBounds: usBounds, maxBoundsViscosity: 1.0,
    layers: [osmLayer], zoomControl: true,
  })
  setTimeout(() => map.invalidateSize(), 200)
}

function renderMap() {
  if (!map || detail.latitude == null || detail.longitude == null) return
  if (marker) { map.removeLayer(marker); marker = null }
  if (impactCircle) { map.removeLayer(impactCircle); impactCircle = null }

  const ll = [detail.latitude, detail.longitude]
  const mVal = _parseEF(detail.ef_scale)
  const color = efColor(detail.ef_scale)

  marker = L.circleMarker(ll, {
    radius: Math.max(10, (mVal + 1) * 4),
    fillColor: color, color: '#1e293b', weight: 3, fillOpacity: 0.9,
  }).addTo(map).bindPopup(
    `<b style="font-size:13px">${buildTitle()}</b><br>${detail.datetime || ''}<br><span style="font-weight:bold;color:${color}">${formatEFLabel(detail.ef_scale)}</span> · 死亡: ${detail.deaths != null ? detail.deaths : '-'} · 受伤: ${detail.injuries != null ? detail.injuries : '-'}`
  ).openPopup()

  impactCircle = L.circle(ll, {
    radius: Math.min((mVal + 1) * 3000, 40000),
    color: color, weight: 2, fillColor: color, fillOpacity: 0.08,
    dashArray: '6,4', bubblingMouseEvents: false,
  }).addTo(map)

  map.setView(ll, Math.min(12, 6 + mVal), { animate: true })
}

// ═══ Canvas：EF 等级频次柱状图 ════════════════════════
const chartCanvas = ref(null)

function drawChart() {
  const cv = chartCanvas.value
  if (!cv) return

  const ctx = cv.getContext('2d')
  const dpr = window.devicePixelRatio || 1
  const rect = cv.getBoundingClientRect()
  if (rect.width === 0 || rect.height === 0) return
  cv.width = rect.width * dpr
  cv.height = rect.height * dpr
  ctx.scale(dpr, dpr)

  const W = rect.width
  const H = rect.height

  // —— 统计数据 ——
  const counts = { EF0: 0, EF1: 0, EF2: 0, EF3: 0, EF4: 0, EF5: 0 }
  const normEF = (raw) => {
    if (raw == null) return ''
    const s = String(raw).trim()
    if (!s) return ''
    // 纯字母+数字格式：F0, F1, ... F5
    var m = s.match(/^F([0-5])$/i)
    if (m) return 'EF' + m[1]
    // 标准：EF0~EF5
    if (/^EF[0-5]$/i.test(s)) return s.toUpperCase()
    // 纯数字：0~5
    if (/^[0-5]$/.test(s)) return 'EF' + s
    // 带 EF 但超出范围或其他格式
    m = s.match(/EF(\d+)/i)
    if (m) { var n = parseInt(m[1]); if (n >= 0 && n <= 5) return 'EF' + n }
    // F6+ 或者无法识别的
    m = s.match(/F(\d+)/i)
    if (m) { var n2 = parseInt(m[1]); if (n2 >= 0 && n2 <= 5) return 'EF' + n2 }
    return ''
  }
  for (const t of nearby.value) {
    const k = normEF(t.ef_scale)
    if (k && k in counts) counts[k]++
  }
  if (detail.ef_scale) {
    const ck = normEF(detail.ef_scale)
    if (ck && ck in counts) counts[ck]++
  }

  const keys = ['EF0', 'EF1', 'EF2', 'EF3', 'EF4', 'EF5']
  const vals = keys.map(k => counts[k])
  const maxVal = Math.max(...vals, 1)

  // —— 布局参数 ——
  const pad = { top: 50, right: 30, bottom: 60, left: 55 }
  const pw = W - pad.left - pad.right
  const ph = H - pad.top - pad.bottom

  const n = 6
  const gap = 16
  const bw = Math.max(52, (pw - gap * (n + 1)) / n)
  const totalW = bw * n + gap * (n - 1)
  const startX = pad.left + (pw - totalW) / 2

  // —— 背景 ——
  ctx.clearRect(0, 0, W, H)
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, W, H)

  // —— Y轴网格线 + 标签 ——
  const ySteps = 5
  ctx.strokeStyle = '#e2e8f0'
  ctx.lineWidth = 1
  for (let i = 0; i <= ySteps; i++) {
    const y = pad.top + (ph / ySteps) * i
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(pad.left + pw, y); ctx.stroke()
  }

  ctx.fillStyle = '#64748b'
  ctx.font = '12px -apple-system, sans-serif'
  ctx.textAlign = 'right'
  for (let i = 0; i <= ySteps; i++) {
    const v = Math.round((maxVal / ySteps) * (ySteps - i))
    const y = pad.top + (ph / ySteps) * i
    ctx.fillText(v.toString(), pad.left - 10, y + 4)
  }

  // —— Y轴标题 ——
  ctx.save()
  ctx.fillStyle = '#94a3b8'
  ctx.font = '11px -apple-system, sans-serif'
  ctx.textAlign = 'center'
  ctx.translate(14, pad.top + ph / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.fillText('频次（次）', 0, 0)
  ctx.restore()

  // —— 柱子 ——
  const barColors = {
    EF0: '#cbd5e1', EF1: '#94a3b8',
    EF2: '#facc15', EF3: '#fb923c',
    EF4: '#f87171', EF5: '#ef4444',
  }
  const curEF = String(detail.ef_scale || '').toUpperCase()

  for (let i = 0; i < n; i++) {
    const k = keys[i]
    const v = vals[i]
    const cx = startX + gap * i + bw * i + bw / 2
    const barH = v > 0 ? (v / maxVal) * ph : 2
    const x = cx - bw / 2
    const y = pad.top + ph - barH

    // 柱子本体 —— 当前等级加粗描边
    const isCurrent = (k === curEF)
    if (isCurrent) {
      // 先画外发光/背景圈
      ctx.fillStyle = barColors[k] + '30'
      ctx.fillRect(x - 3, y - 3, bw + 6, barH + 3)
      ctx.strokeStyle = '#1e40af'
      ctx.lineWidth = 3
      ctx.strokeRect(x - 3, y - 3, bw + 6, barH + 3)
      ctx.lineWidth = 1
    }

    ctx.fillStyle = barColors[k]
    ctx.fillRect(x, y, bw, barH)

    // —— 数值标注：始终在柱子内部偏上位置，高柱在柱内，矮柱在柱顶上方 ——
    const numberFont = 'bold 14px -apple-system, sans-serif'
    const labelY = barH > 28 ? y + 22 : y - 10  // 高柱→内部 矮柱→上方

    ctx.fillStyle = barH > 28 ? '#1e293b' : '#0f172a'
    ctx.font = numberFont
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(v.toString(), cx, labelY)
    ctx.textBaseline = 'alphabetic'

    // —— X轴等级标签 ——
    ctx.fillStyle = '#334155'
    ctx.font = 'bold 13px -apple-system, sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(k, cx, H - 12)

    // —— 当前等级底部星标 ——
    if (isCurrent) {
      ctx.fillStyle = '#1e40af'
      ctx.font = 'bold 12px -apple-system, sans-serif'
      ctx.fillText('★ 本事件', cx, H - 32)
    }
  }

  // —— 底部数据来源 ——
  ctx.fillStyle = '#94a3b8'
  ctx.font = '11px -apple-system, sans-serif'
  ctx.textAlign = 'left'
  ctx.fillText(
    `数据来源：NOAA SPC · ${detail.province || '同州'}及周边`,
    pad.left + 2, H - 42
  )
}

// ═══ AI 分析 ═════════════════════════════════════════
const analysisTypes = [
  { value: 'trend', label: '活动趋势', icon: 'fa fa-signal' },
  { value: 'risk', label: '风险评估', icon: 'fa fa-exclamation-triangle' },
  { value: 'climate', label: '气候特征', icon: 'fa fa-globe' },
]
const selectedAnalysis = ref('trend')
const aiResult = ref('')
const aiCached = ref(false)
const aiLoading = ref(false)

async function runAIAnalysis() {
  aiResult.value = ''; aiCached.value = false; aiLoading.value = true
  try {
    const { data: r } = await api.post(
      '/api/tornado/ai_analysis',
      { event_id: eventId, analysis_type: selectedAnalysis.value },
      { timeout: 90000 }
    )
    if (r.code === 200) { aiResult.value = r.data.content; aiCached.value = !!r.data.cached }
    else aiResult.value = '分析失败：' + (r.message || '未知错误')
  } catch (e) {
    aiResult.value = 'AI 分析请求失败，请检查网络连接后重试'
  } finally { aiLoading.value = false }
}

async function clearCache() {
  try {
    await api.delete('/api/tornado/ai_cache', {data: {event_id: eventId, analysis_type: selectedAnalysis.value}});
    aiResult.value = ''; aiCached.value = false;
  } catch (e) { console.error(e); }
}

// ═══ 数据加载 ═════════════════════════════════════════
async function fetchData() {
  try {
    const { data: r } = await api.get(`/api/tornado/${eventId}`)
    if (r.code === 200 && r.data) {
      const info = r.data.detail || {}
      Object.assign(detail, info);
      // 安全处理可为 null 的数值字段
      detail.casualties = info.casualties != null ? info.casualties : null;
      detail.deaths = info.deaths != null ? info.deaths : null
      detail.injuries = info.injuries != null ? info.injuries : null
      detail.damage = info.damage || ''
      nearby.value = r.data.nearby || []
      spatialStats.value = r.data.spatial_stats || null
    }
  } catch (e) { console.error('获取龙卷风详情失败:', e) }
}

// ═══ 生命周期 ═════════════════════════════════════════
let resizeObserver = null

onMounted(async () => {
  await fetchData()
  mapLoading.value = false
  await nextTick()
  initMap()
  renderMap()
  drawChart()
  resizeObserver = new ResizeObserver(() => drawChart())
  const el = chartCanvas.value?.parentElement
  if (el) resizeObserver.observe(el)
})

onUnmounted(() => {
  if (map) { map.remove(); map = null }
  if (resizeObserver) { resizeObserver.disconnect(); resizeObserver = null }
})
</script>

<style>
.delay-150 { animation-delay: .15s }
.delay-300 { animation-delay: .3s }
#tornado-map .leaflet-container { background: #f0f0f0 }
#tornado-map .leaflet-control-zoom a {
  background: #1e293b; color: #e2e8f0; border-color: #334155; border-radius: 6px;
}
#tornado-map .leaflet-control-zoom a:hover { background: #334155 }
#tornado-map .leaflet-control-attribution {
  background: rgba(15, 23, 42, 0.8); color: #94a3b8; font-size: 10px; padding: 2px 8px;
}
#tornado-map .leaflet-popup-content-wrapper {
  background: rgba(30, 41, 59, 0.95); color: #e2e8f0; border-radius: 12px;
  backdrop-filter: blur(12px); padding: 8px 12px;
}
#tornado-map .leaflet-popup-tip { background: rgba(30, 41, 59, 0.95) }
#tornado-map .leaflet-popup-content { margin: 4px 0; line-height: 1.6 }
</style>
