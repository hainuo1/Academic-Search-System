<template>
<div class="min-h-screen bg-slate-50">

  <div class="bg-gradient-to-r from-slate-800 via-indigo-900 to-blue-950 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">
      <button @click="$router.push('/earthquake')"
        class="text-slate-300 hover:text-white transition-colors mb-3 flex items-center gap-1.5 text-sm">
        <i class="fa fa-arrow-left"></i>返回地震列表
      </button>
      <div class="flex items-center gap-3">
        <h1 class="text-2xl md:text-3xl font-bold">{{ detail.place?.substring(0,60) || detail.event_id }}</h1>
        <span :class="magBadgeClass(detail.magnitude)" class="px-3 py-1 rounded-full text-sm font-bold">
          M{{ (detail.magnitude||0).toFixed(1) }}
        </span>
      </div>
      <p class="text-slate-300 mt-1 text-sm">
        {{ detail.datetime }} · 震源深度 {{ detail.depth }}km · {{ detail.mag_type || 'N/A' }}
      </p>
    </div>
  </div>

  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">

    <div class="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ (detail.magnitude||0).toFixed(1) }}</div>
        <div class="text-xs text-slate-500 mt-1">震级（M）</div>
        <div class="text-[11px] text-slate-400 mt-0.5">释放能量大小</div>
      </div>
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ detail.depth }}</div>
        <div class="text-xs text-slate-500 mt-1">震源深度（km）</div>
        <div class="text-[11px] text-slate-400 mt-0.5">越大震感范围越广</div>
      </div>
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ detail.nst || '未记录' }}</div>
        <div class="text-xs text-slate-500 mt-1">定位台站</div>
        <div class="text-[11px] text-slate-400 mt-0.5">记录到该事件的台站数</div>
      </div>
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ detail.horizontal_error ? detail.horizontal_error.toFixed(1)+'km' : '未记录' }}</div>
        <div class="text-xs text-slate-500 mt-1">水平误差</div>
        <div class="text-[11px] text-slate-400 mt-0.5">越小定位越精确</div>
      </div>
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ detail.rms ? detail.rms.toFixed(2) : '未记录' }}</div>
        <div class="text-xs text-slate-500 mt-1">定位残差（RMS）</div>
        <div class="text-[11px] text-slate-400 mt-0.5">越小定位越精确</div>
      </div>
    </div>

    <!-- 1. 震中位置地图 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-map-o text-amber-500"></i>
        <span class="font-semibold text-slate-700">震中位置</span>
      </div>
      <div class="relative">
        <div id="earthquake-map" style="height: 480px;"></div>
        <div v-if="mapLoading" class="absolute inset-0 bg-white/60 flex items-center justify-center">
          <div class="text-center">
            <div class="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p class="text-slate-500 text-sm mt-2">加载中...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. 区域地震活动柱状图 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-bar-chart text-indigo-500"></i>
        <span class="font-semibold text-slate-700">区域地震活动（±3°范围）</span>
        <span class="text-xs text-slate-400 ml-auto" id="eq-trend-tooltip">鼠标悬停查看详情</span>
      </div>
      <div class="relative p-2">
        <canvas ref="trendCanvas" style="width:100%;height:400px"></canvas>
      </div>
    </div>

    <!-- 3. 事件属性雷达对比 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-star-o text-amber-500"></i>
        <span class="font-semibold text-slate-700">事件属性对比雷达图</span>
        <span class="text-xs text-slate-400 ml-auto">当前事件 vs 区域历史均值</span>
      </div>
      <div class="relative p-2">
        <canvas ref="radarCanvas" style="width:100%;height:540px"></canvas>
      </div>
    </div>

    <!-- 4. AI 分析 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-magic text-purple-500"></i>
        <span class="font-semibold text-slate-700">AI 科学分析</span>
      </div>
      <div class="p-5">
        <div class="flex flex-wrap gap-2 mb-4">
          <button v-for="opt in analysisTypes" :key="opt.value"
            @click="selectedAnalysis = opt.value; aiResult = ''"
            :class="selectedAnalysis === opt.value ? 'bg-indigo-600 text-white shadow-md' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
            class="px-4 py-2 rounded-xl text-sm font-medium transition-all">
            {{ opt.label }}
          </button>
          <div class="flex-1"></div>
          <button @click="clearCache" :disabled="aiLoading"
            class="px-4 py-2 bg-red-50 border border-red-200 text-red-500 rounded-xl text-sm font-medium hover:bg-red-100 transition-colors disabled:opacity-50 flex items-center gap-1.5">
            <i class="fa fa-trash-o"></i>清理缓存
          </button>
          <button @click="runAIAnalysis" :disabled="aiLoading"
            class="px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl text-sm font-medium hover:shadow-lg disabled:opacity-60 flex items-center gap-2">
            <i :class="aiLoading ? 'fa fa-spinner fa-spin' : 'fa fa-play'"></i>
            {{ aiLoading ? '分析中...' : '开始分析' }}
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
          <div class="inline-flex gap-2 text-indigo-600">
            <div class="w-2 h-2 bg-indigo-600 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-indigo-600 rounded-full animate-bounce delay-150"></div>
            <div class="w-2 h-2 bg-indigo-600 rounded-full animate-bounce delay-300"></div>
          </div>
          <p class="text-slate-500 text-sm mt-3">DeepSeek 分析中...</p>
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

let map = null, marker = null

function magBadgeClass(m) { return m>=7?'bg-red-100 text-red-700':m>=6?'bg-orange-100 text-orange-700':m>=5?'bg-amber-100 text-amber-700':'bg-blue-100 text-blue-700' }

// ═══ 地图 ═══
function initMap() {
  if (map) return
  map = L.map('earthquake-map', {
    center: [35, 104], zoom: 5, minZoom: 4,
    maxBounds: [[10, 65], [55, 140]], maxBoundsViscosity: 0.8,
    layers: [L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scale=1&style=8', { subdomains: ['1','2','3','4'], maxZoom: 10 })]
  })
  setTimeout(() => map.invalidateSize(), 200)
}
function renderMap() {
  if (!map || !detail.latitude) return
  if (marker) map.removeLayer(marker)
  const ll = [detail.latitude, detail.longitude]
  const r = Math.max(6, (detail.magnitude||4)*5)
  const c = detail.magnitude>=7?'#ef4444':detail.magnitude>=6?'#f97316':detail.magnitude>=5?'#eab308':'#3b82f6'
  marker = L.circleMarker(ll, { radius:r, fillColor:c, color:'#fff', weight:2, fillOpacity:0.8 })
    .addTo(map).bindPopup(`<b>${detail.place}</b><br>${detail.datetime}<br>M${(detail.magnitude||0).toFixed(1)} · ${detail.depth}km`).openPopup()
  L.circle(ll, { radius:Math.min((detail.depth||10)*1500,300000), color:'#f59e0b', weight:1, fillColor:'#f59e0b', fillOpacity:0.06, dashArray:'4,4', bubblingMouseEvents:false }).addTo(map)
  map.setView(ll, 7)
}

// ═══ 柱状图（区域地震活动） ═══
const trendCanvas = ref(null)
function drawTrend() {
  const cv = trendCanvas.value; if(!cv||nearby.value.length===0) return
  const ctx = cv.getContext('2d'), dpr = window.devicePixelRatio||1, rect = cv.getBoundingClientRect()
  if (rect.width < 10 || rect.height < 10) return
  cv.width = rect.width*dpr; cv.height = rect.height*dpr; ctx.scale(dpr,dpr)
  const W = rect.width, H = rect.height; ctx.clearRect(0,0,W,H)

  // 组装数据：邻近事件 + 当前事件，按时序排列
  const curPt = {datetime: detail.datetime, magnitude: detail.magnitude || 0, place: detail.place, isCurrent: true}
  const allPts = [...nearby.value.map(d=>({...d, isCurrent: false})), curPt]
    .sort((a,b)=> new Date(a.datetime) - new Date(b.datetime))
  const n = allPts.length; if(n<2) return

  const pad = {top: 22, right: 22, bottom: 80, left: 55}
  const pw = W - pad.left - pad.right, ph = H - pad.top - pad.bottom
  const mags = allPts.map(d=>d.magnitude||0)
  const mMax = Math.max(...mags), mMin = Math.min(...mags)
  const yMax = mMax + 0.8, yMin = Math.max(0, mMin - 0.5)

  const tX = i => pad.left + (i/(n-1)) * pw
  const tY = v => pad.top + ph - ((v - yMin)/(yMax - yMin)) * ph

  // 网格
  ctx.strokeStyle='#f1f5f9'; ctx.lineWidth=1
  for(let i=0;i<=5;i++) {
    let y = pad.top + (ph/5)*i
    ctx.beginPath(); ctx.moveTo(pad.left,y); ctx.lineTo(pad.left+pw,y); ctx.stroke()
  }
  // Y轴标签
  ctx.fillStyle='#64748b'; ctx.font='10px sans-serif'; ctx.textAlign='right'
  for(let i=0;i<=5;i++) {
    let v = yMin + ((yMax-yMin)/5)*i
    ctx.fillText(v.toFixed(1), pad.left-8, tY(v)+4)
  }

  // 柱状：当前红色、邻近金色，宽度按数据量自动适配
  const barW = Math.max(2, Math.min(pw / n * 0.7, 12))
  const gap = (pw / n - barW) / 2

  for(let i=0;i<n;i++) {
    let d = allPts[i]
    let h = Math.max(2, tY(yMin) - tY(d.magnitude))
    let x = tX(i) - barW/2, y = tY(d.magnitude)
    ctx.fillStyle = d.isCurrent ? '#ef4444' : '#f59e0b'
    ctx.globalAlpha = d.isCurrent ? 1 : 0.65
    ctx.fillRect(x, y, barW, h)
    ctx.globalAlpha = 1
  }

  // X轴：只标注起止年份 + 当前事件位置
  ctx.fillStyle='#94a3b8'; ctx.font='9px sans-serif'; ctx.textAlign='center'
  let firstYr = new Date(allPts[0].datetime).getFullYear()
  let lastYr = new Date(allPts[n-1].datetime).getFullYear()
  ctx.fillText(String(firstYr), tX(0), H - 58)
  ctx.fillText(String(lastYr), tX(n-1), H - 58)
  // 中间标当前事件年份
  for(let i=0;i<n;i++) {
    if(allPts[i].isCurrent) {
      let yr = new Date(allPts[i].datetime).getFullYear()
      ctx.fillStyle = '#ef4444'; ctx.font = 'bold 11px sans-serif'
      ctx.fillText(String(yr), tX(i), H - 42)
      break
    }
  }

  // X轴下方说明
  ctx.fillStyle='#64748b'; ctx.font = '9px sans-serif'; ctx.textAlign = 'left'
  ctx.fillText('红色=当前事件  金色=邻近事件', pad.left+2, H - 20)
  ctx.fillText('区域范围：±3°（纬度  '+detail.latitude?.toFixed(1)+'°/经度  '+detail.longitude?.toFixed(1)+'°）', pad.left+2, H - 6)

  // 鼠标悬停
  cv.onmousemove = e => {
    let idx = Math.round(((e.offsetX - pad.left) / pw) * (n-1))
    if(idx<0||idx>=n) return
    let d = allPts[idx]
    let tip = document.getElementById('eq-trend-tooltip')
    if(tip) tip.textContent = d.datetime + ' | M' + (d.magnitude||0).toFixed(1) + ' | ' + (d.place||'').substring(0,40)
  }
  cv.onmouseleave = () => {
    let tip = document.getElementById('eq-trend-tooltip')
    if(tip) tip.textContent = '鼠标悬停查看详情'
  }
}

// ═══ 雷达图（当前事件 vs 区域均值） ═══
const radarCanvas = ref(null)
function drawRadar() {
  const cv = radarCanvas.value; if(!cv) return
  const ctx = cv.getContext('2d'), dpr = window.devicePixelRatio||1, rect = cv.getBoundingClientRect()
  cv.width = rect.width*dpr; cv.height = rect.height*dpr; ctx.scale(dpr,dpr)
  const W = rect.width, H = rect.height; ctx.clearRect(0,0,W,H)

  // 维度定义：5个维度，标签与5卡指标一致
  const dims = ['震级', '震源深度', '定位台站', '水平误差', '定位残差']
  // 安全均值：只计算有效值，避免未记录数据拉低均值
  const safeAvg = key => {
    const vals = nearby.value.map(d=>d[key]).filter(v => v != null && v !== 0)
    return vals.length ? vals.reduce((a,b)=>a+b,0)/vals.length : null
  }

  // 当前事件的5个值（null/0 视为未记录）
  const curVals = [
    {key:'magnitude', val:detail.magnitude||0, scale:10,  fmt:v=>v.toFixed(1)},
    {key:'depth',      val:detail.depth||0,     scale:300, fmt:v=>v+' km'},
    {key:'nst',        val:detail.nst||0,       scale:300, fmt:v=>'nst='+v},
    {key:'horizontal_error', val:detail.horizontal_error||0, scale:20, fmt:v=>v.toFixed(1)+' km'},
    {key:'rms',        val:detail.rms||0,       scale:2,   fmt:v=>v.toFixed(2)},
  ]

  // 区域均值（只从有效值计算，没数据则为 null）
  const avgVals = curVals.map(d => {
    const a = safeAvg(d.key)
    return a !== null ? {val:a, hasAvg:true} : {val:0, hasAvg:false}
  })

  const n = 5, cx = W/2, cy = H/2 + 5
  const rad = Math.min(cx, cy) - 80
  const _norm = (v, sc) => Math.min((v||0)/sc, 1)
  const _boost = v => Math.pow(v, 0.55)

  // 区域平均多边形（蓝色虚线）
  ctx.beginPath()
  let hasAvg = false
  for(let i=0;i<n;i++){
    if(!avgVals[i].hasAvg) continue
    let r = rad * _boost(_norm(avgVals[i].val, curVals[i].scale))
    let a=(Math.PI*2/n)*i-Math.PI/2, x=cx+Math.cos(a)*r, y=cy+Math.sin(a)*r
    hasAvg ? ctx.lineTo(x,y) : ctx.moveTo(x,y)
    hasAvg = true
  }
  if(hasAvg){
    ctx.closePath()
    ctx.fillStyle='rgba(59,130,246,0.12)'; ctx.fill()
    ctx.strokeStyle='#3b82f6'; ctx.lineWidth=2; ctx.setLineDash([8,4]); ctx.stroke(); ctx.setLineDash([])
  }

  // 当前事件多边形（红色实线）
  ctx.beginPath()
  let hasCur = false
  for(let i=0;i<n;i++){
    let v = curVals[i].val, r
    if(v === 0) r = 0
    else r = Math.max(2, rad * _boost(_norm(v, curVals[i].scale)))
    let a=(Math.PI*2/n)*i-Math.PI/2, x=cx+Math.cos(a)*r, y=cy+Math.sin(a)*r
    hasCur ? ctx.lineTo(x,y) : ctx.moveTo(x,y)
    hasCur = true
  }
  ctx.closePath()
  ctx.fillStyle='rgba(239,68,68,0.08)'; ctx.fill()
  ctx.strokeStyle='#ef4444'; ctx.lineWidth=2.5; ctx.stroke()

  // 网格环
  for(let ring=1;ring<=4;ring++){
    ctx.beginPath()
    for(let i=0;i<n;i++){
      let a=(Math.PI*2/n)*i-Math.PI/2, r=(rad/4)*ring
      let x=cx+Math.cos(a)*r, y=cy+Math.sin(a)*r
      i===0?ctx.moveTo(x,y):ctx.lineTo(x,y)
    }
    ctx.closePath()
    ctx.strokeStyle=ring===4?'#cbd5e1':'#f1f5f9'; ctx.lineWidth=ring===4?1.5:0.7; ctx.stroke()
  }

  // 五个角：维度标签放到远端，数据值（大字号）嵌在顶点处
  for(let i=0;i<n;i++){
    let v = curVals[i].val, r
    if(v === 0) r = 0
    else r = Math.max(2, rad * _boost(_norm(v, curVals[i].scale)))
    let a=(Math.PI*2/n)*i-Math.PI/2
    let x=cx+Math.cos(a)*r, y=cy+Math.sin(a)*r

    // 顶点圆点
    ctx.beginPath(); ctx.arc(x,y,5,0,Math.PI*2)
    ctx.fillStyle=v===0?'#94a3b8':'#ef4444'; ctx.fill()
    ctx.strokeStyle='#fff'; ctx.lineWidth=2; ctx.stroke()

    // 数据值：大字号，嵌在顶点外紧贴（+10px），永远在雷达区域内
    let raw = v===0 ? '未记录' : curVals[i].fmt(v)
    let vx = cx + Math.cos(a) * (r + 12), vy = cy + Math.sin(a) * (r + 12)
    ctx.fillStyle=v===0?'#94a3b8':'#b91c1c'
    ctx.font = v===0 ? '10px sans-serif' : 'bold 15px sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(raw, vx, vy)

    // 维度标签：推到很远的外圈（+38px），绝不和数据重叠
    let dx = cx + Math.cos(a) * (rad + 38), dy = cy + Math.sin(a) * (rad + 38)
    ctx.fillStyle='#1e293b'; ctx.font='bold 12px sans-serif'
    ctx.textAlign='center'
    ctx.textBaseline = 'middle'
    // 小引导线从最外环连到标签
    ctx.beginPath()
    ctx.moveTo(cx+Math.cos(a)*rad, cy+Math.sin(a)*rad)
    ctx.lineTo(dx, dy)
    ctx.strokeStyle='#e2e8f0'; ctx.lineWidth=0.5; ctx.stroke()
    ctx.fillText(dims[i], dx, dy)
  }

  // 图例 —— 全部放在左上角，加粗加大
  let lx = 14, ly = 20
  // 当前事件
  ctx.strokeStyle='#ef4444'; ctx.lineWidth=4; ctx.setLineDash([])
  ctx.beginPath(); ctx.moveTo(lx, ly); ctx.lineTo(lx+24, ly); ctx.stroke()
  ctx.fillStyle = '#1e293b'; ctx.font = 'bold 14px sans-serif'; ctx.textAlign = 'left'
  ctx.fillText('当前事件', lx+32, ly+5)
  ctx.fillStyle = '#64748b'; ctx.font = '11px sans-serif'
  ctx.fillText('（红色实线 · 灰点为未记录）', lx+32, ly+24)

  // 区域均值
  ly += 44
  ctx.strokeStyle='#3b82f6'; ctx.lineWidth=2.5; ctx.setLineDash([6,3])
  ctx.beginPath(); ctx.moveTo(lx, ly); ctx.lineTo(lx+24, ly); ctx.stroke(); ctx.setLineDash([])
  ctx.fillStyle = '#1e293b'; ctx.font = 'bold 14px sans-serif'
  ctx.fillText('区域均值', lx+32, ly+5)
  ctx.fillStyle = '#64748b'; ctx.font = '11px sans-serif'
  ctx.fillText('（蓝色虚线 = 周边 ±3° 有效均值）', lx+32, ly+24)
}

let cro = null

// ═══ AI ═══
const analysisTypes = [
  { value:'trend', label:'活动趋势' },
  { value:'risk',  label:'风险评估' },
  { value:'impact',label:'影响分析' },
]
const selectedAnalysis = ref('trend'), aiResult = ref(''), aiCached = ref(false), aiLoading = ref(false)
async function runAIAnalysis() {
  aiResult.value=''; aiCached.value=false; aiLoading.value=true
  try {
    let {data:r} = await api.post('/api/earthquake/ai_analysis', {event_id:eventId, analysis_type:selectedAnalysis.value}, {timeout:90000})
    if(r.code===200){aiResult.value=r.data.content; aiCached.value=!!r.data.cached}
    else aiResult.value='❌ '+r.message
  } catch(e) {aiResult.value='❌ 请求失败'}
  finally {aiLoading.value=false}
}

async function clearCache() {
  try {
    await api.delete('/api/earthquake/ai_cache', {data: {event_id: eventId, analysis_type: selectedAnalysis.value}})
    aiResult.value = ''; aiCached.value = false
  } catch (e) { console.error(e) }
}

async function fetchData() {
  try {
    let r = await api.get(`/api/earthquake/${eventId}`)
    if(r.data.code===200){Object.assign(detail,r.data.data.detail); nearby.value=r.data.data.nearby}
  } catch(e) {console.error(e)}
}

onMounted(async () => {
  await fetchData(); mapLoading.value = false
  await nextTick(); initMap(); renderMap()
  drawTrend(); drawRadar()
  cro = new ResizeObserver(()=>{drawTrend(); drawRadar()})
  let el = trendCanvas.value?.parentElement; if(el) cro.observe(el)
})
onUnmounted(() => { map?.remove(); map = null; cro?.disconnect() })
</script>

<style>
.delay-150{animation-delay:.15s}.delay-300{animation-delay:.3s}
#earthquake-map .leaflet-container{background:#e8e8e8}
#earthquake-map .leaflet-control-zoom a{background:#1e293b;color:#e2e8f0;border-color:#334155}
#earthquake-map .leaflet-control-attribution{background:rgba(15,23,42,.75);color:#64748b;font-size:10px}
#earthquake-map .leaflet-popup-content-wrapper{background:rgba(30,41,59,.94);color:#e2e8f0;border-radius:12px}
#earthquake-map .leaflet-popup-tip{background:rgba(30,41,59,.94)}
</style>
