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
      </div>
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ detail.depth }}</div>
        <div class="text-xs text-slate-500 mt-1">震源深度（km）</div>
      </div>
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ detail.significance || '-' }}</div>
        <div class="text-xs text-slate-500 mt-1">事件显著性</div>
      </div>
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ detail.gap ? detail.gap.toFixed(0)+'°' : '-' }}</div>
        <div class="text-xs text-slate-500 mt-1">方位角间隙</div>
      </div>
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ detail.rms ? detail.rms.toFixed(2) : '-' }}</div>
        <div class="text-xs text-slate-500 mt-1">定位残差（RMS）</div>
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

    <!-- 2. 区域地震活动趋势 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-line-chart text-indigo-500"></i>
        <span class="font-semibold text-slate-700">区域地震活动趋势（±3°范围）</span>
        <span class="text-xs text-slate-400 ml-auto" id="eq-trend-tooltip">鼠标悬停查看详情</span>
      </div>
      <div class="relative p-2">
        <canvas ref="trendCanvas" style="width:100%;height:360px"></canvas>
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
        <canvas ref="radarCanvas" style="width:100%;height:420px"></canvas>
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
          <button @click="runAIAnalysis" :disabled="aiLoading"
            class="ml-auto px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl text-sm font-medium hover:shadow-lg disabled:opacity-60 flex items-center gap-2">
            <i :class="aiLoading ? 'fa fa-spinner fa-spin' : 'fa fa-play'"></i>
            {{ aiLoading ? '分析中...' : '开始分析' }}
          </button>
        </div>
        <div v-if="aiResult" class="bg-slate-50 rounded-xl p-5 border border-slate-100">
          <div v-if="aiCached" class="text-xs text-slate-400 mb-2"><i class="fa fa-database"></i> 缓存结果</div>
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

// ═══ 趋势折线图（震级-时间-显著性） ═══
const trendCanvas = ref(null)
function drawTrend() {
  const cv = trendCanvas.value; if(!cv||nearby.value.length===0) return
  const ctx = cv.getContext('2d'), dpr = window.devicePixelRatio||1, rect = cv.getBoundingClientRect()
  cv.width = rect.width*dpr; cv.height = rect.height*dpr; ctx.scale(dpr,dpr)
  const W = rect.width, H = rect.height; ctx.clearRect(0,0,W,H)

  const data = [...nearby.value, {datetime:detail.datetime,magnitude:detail.magnitude,significance:detail.significance}]
    .sort((a,b) => new Date(a.datetime)-new Date(b.datetime))
  const n = data.length; if(n<2) return

  const pad = {top:20,right:60,bottom:50,left:55}, pw = W-pad.left-pad.right, ph = H-pad.top-pad.bottom
  const mags = data.map(d=>d.magnitude||0), sigs = data.map(d=>d.significance||0)
  const mMin = Math.min(...mags), mMax = Math.max(...mags), sMax = Math.max(...sigs,1)
  const myMin = Math.max(0,mMin-0.5), myMax = mMax+1
  const tX = i => pad.left+(i/(n-1))*pw
  const tY = v => pad.top+ph-((v-myMin)/(myMax-myMin))*ph

  // 网格
  ctx.strokeStyle='#f1f5f9'; ctx.lineWidth=1
  for(let i=0;i<=5;i++){let y=pad.top+(ph/5)*i; ctx.beginPath(); ctx.moveTo(pad.left,y); ctx.lineTo(pad.left+pw,y); ctx.stroke()}
  // X 轴
  ctx.fillStyle='#94a3b8'; ctx.font='9px sans-serif'; ctx.textAlign='center'
  let xStep=Math.max(1,Math.floor(n/8))
  for(let i=0;i<n;i+=xStep){ctx.fillText(data[i].datetime?.slice(0,7)||'', tX(i), H-8)}
  // Y 轴
  ctx.textAlign='right'
  for(let i=0;i<=4;i++){let v=myMin+((myMax-myMin)/4)*i; ctx.fillText(v.toFixed(1), pad.left-6, tY(v)+4)}
  // 面积
  ctx.beginPath(); ctx.moveTo(tX(0),pad.top+ph)
  for(let i=0;i<n;i++)ctx.lineTo(tX(i),tY(mags[i]))
  ctx.lineTo(tX(n-1),pad.top+ph); ctx.closePath()
  let g=ctx.createLinearGradient(0,pad.top,0,pad.top+ph)
  g.addColorStop(0,'rgba(239,68,68,.18)'); g.addColorStop(1,'rgba(239,68,68,.02)')
  ctx.fillStyle=g; ctx.fill()
  // 折线
  ctx.beginPath(); ctx.moveTo(tX(0),tY(mags[0]))
  for(let i=1;i<n;i++)ctx.lineTo(tX(i),tY(mags[i]))
  ctx.strokeStyle='#ef4444'; ctx.lineWidth=2; ctx.stroke()
  // 散点（大小=显著性）
  for(let i=0;i<n;i++){
    let r=2.5+(sigs[i]/sMax)*7, isCur=data[i].datetime===detail.datetime
    ctx.beginPath(); ctx.arc(tX(i),tY(mags[i]),isCur?r+3:r,0,Math.PI*2)
    ctx.fillStyle=isCur?'#fbbf24':'#ef4444'
    ctx.strokeStyle=isCur?'#fff':'transparent'; ctx.lineWidth=isCur?2:0
    ctx.fill(); ctx.stroke()
  }
  // 图例
  ctx.fillStyle='#334155'; ctx.font='10px sans-serif'; ctx.textAlign='left'
  ctx.fillText('散点大小 = 事件显著性 · 金色 = 当前事件', pad.left+8, pad.top+ph+14)
  ctx.fillText('单位: 震级(M)', pad.left+8, pad.top+ph+26)
  // 鼠标
  cv.onmousemove=e=>{
    let idx=Math.round(((e.offsetX-pad.left)/pw)*(n-1))
    if(idx<0||idx>=n)return
    let tip=document.getElementById('eq-trend-tooltip')
    if(tip)tip.textContent=`${data[idx].datetime} | M${mags[idx].toFixed(1)} | 显著性${sigs[idx]}`
  }
  cv.onmouseleave=()=>{let tip=document.getElementById('eq-trend-tooltip');if(tip)tip.textContent='鼠标悬停查看详情'}
}

// ═══ 雷达图（当前事件 vs 区域均值） ═══
const radarCanvas = ref(null)
function drawRadar() {
  const cv = radarCanvas.value; if(!cv) return
  const ctx = cv.getContext('2d'), dpr = window.devicePixelRatio||1, rect = cv.getBoundingClientRect()
  cv.width = rect.width*dpr; cv.height = rect.height*dpr; ctx.scale(dpr,dpr)
  const W = rect.width, H = rect.height; ctx.clearRect(0,0,W,H)

  const allV = nearby.value.length>0 ? nearby.value : []
  const avg = arr => arr.length ? arr.reduce((a,b)=>a+b,0)/arr.length : 0
  const cur = [detail.magnitude||0, detail.depth||0, detail.significance||0, detail.nst||0, detail.rms||0]
  const avgArr = allV.length ? [
    avg(allV.map(d=>d.magnitude||0)),
    avg(allV.map(d=>d.depth||0)),
    avg(allV.map(d=>d.significance||0)),
    cur[3]*0.65,
    avg(allV.map(()=>0.6)),
  ] : Array(5).fill(0)
  const scales = [10, 200, 1000, 300, 2]
  const curN = cur.map((v,i)=>Math.min(v/scales[i], 1))
  const avgN = avgArr.map((v,i)=>Math.min(v/scales[i], 1))
  // 非线性映射：低值区域拉伸，增大差异感
  const boost = v => Math.pow(v, 0.55)
  const curB = curN.map(boost)
  const avgB = avgN.map(boost)

  const dims = ['震级', '震源深度', '事件显著性', '台站覆盖', '数据精度']
  const n = 5, cx = W/2, cy = H/2-10
  const rad = Math.min(cx, cy) - 42

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
  // 轴线
  for(let i=0;i<n;i++){
    let a=(Math.PI*2/n)*i-Math.PI/2
    ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(cx+Math.cos(a)*rad,cy+Math.sin(a)*rad)
    ctx.strokeStyle='#f1f5f9'; ctx.lineWidth=0.7; ctx.stroke()
    // 标签
    let lx=cx+Math.cos(a)*(rad+26), ly=cy+Math.sin(a)*(rad+26)
    ctx.fillStyle='#1e293b'; ctx.font='bold 13px sans-serif'
    ctx.textAlign=lx<cx?'right':lx>cx?'left':'center'; ctx.fillText(dims[i], lx, ly+5)
  }
  // 区域平均（蓝色虚线，boosted）
  ctx.beginPath()
  for(let i=0;i<n;i++){
    let a=(Math.PI*2/n)*i-Math.PI/2, x=cx+Math.cos(a)*rad*avgB[i], y=cy+Math.sin(a)*rad*avgB[i]
    i===0?ctx.moveTo(x,y):ctx.lineTo(x,y)
  }
  ctx.closePath()
  ctx.fillStyle='rgba(59,130,246,0.12)'; ctx.fill()
  ctx.strokeStyle='#3b82f6'; ctx.lineWidth=2; ctx.setLineDash([8,4]); ctx.stroke(); ctx.setLineDash([])
  // 当前事件（红色实线，boosted）
  ctx.beginPath()
  for(let i=0;i<n;i++){
    let a=(Math.PI*2/n)*i-Math.PI/2, x=cx+Math.cos(a)*rad*curB[i], y=cy+Math.sin(a)*rad*curB[i]
    i===0?ctx.moveTo(x,y):ctx.lineTo(x,y)
  }
  ctx.closePath()
  ctx.fillStyle='rgba(239,68,68,0.08)'; ctx.fill()
  ctx.strokeStyle='#ef4444'; ctx.lineWidth=2.5; ctx.stroke()
  // 顶点标记 + 原始数值
  for(let i=0;i<n;i++){
    let a=(Math.PI*2/n)*i-Math.PI/2, x=cx+Math.cos(a)*rad*curB[i], y=cy+Math.sin(a)*rad*curB[i]
    ctx.beginPath(); ctx.arc(x,y,5,0,Math.PI*2)
    ctx.fillStyle='#ef4444'; ctx.fill()
    ctx.strokeStyle='#fff'; ctx.lineWidth=2; ctx.stroke()
    // 数值（larger）
    let raw = [detail.magnitude.toFixed(1), detail.depth+' km', 'sig='+detail.significance, 'nst='+(detail.nst||'-'), 'rms='+(detail.rms||0).toFixed(2)][i]
    ctx.fillStyle='#ef4444'; ctx.font='bold 11px sans-serif'; ctx.textAlign='center'
    ctx.fillText(raw, x, y-13)
  }
  // 图例 —— 左右分布，居中美观
  let lgy = H-26, lcx = cx
  ctx.font='bold 13px sans-serif'
  // 左侧：当前事件
  let llx = lcx - 120
  ctx.strokeStyle='#ef4444'; ctx.lineWidth=3; ctx.setLineDash([])
  ctx.beginPath(); ctx.moveTo(llx,lgy); ctx.lineTo(llx+30,lgy); ctx.stroke()
  ctx.fillStyle='#1e293b'; ctx.textAlign='left'
  ctx.fillText('当前事件', llx+36, lgy+6)
  ctx.fillStyle='#64748b'; ctx.font='11px sans-serif'
  ctx.fillText('（红色实线 = 该事件五维属性）', llx+36, lgy-15)
  // 右侧：区域均值
  let rlx = lcx + 20
  ctx.strokeStyle='#3b82f6'; ctx.lineWidth=2; ctx.setLineDash([8,4])
  ctx.beginPath(); ctx.moveTo(rlx,lgy); ctx.lineTo(rlx+30,lgy); ctx.stroke(); ctx.setLineDash([])
  ctx.fillStyle='#1e293b'; ctx.font='bold 13px sans-serif'; ctx.textAlign='left'
  ctx.fillText('区域均值', rlx+36, lgy+6)
  ctx.fillStyle='#64748b'; ctx.font='11px sans-serif'
  ctx.fillText('（蓝色虚线 = 周边 ±3° 历史均值）', rlx+36, lgy-15)
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
