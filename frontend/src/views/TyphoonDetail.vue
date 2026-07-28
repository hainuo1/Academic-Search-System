<template>
<div class="min-h-screen bg-slate-50">

  <div class="bg-gradient-to-r from-slate-800 to-indigo-900 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">
      <button @click="$router.push('/typhoon')"
        class="text-slate-300 hover:text-white transition-colors mb-3 flex items-center gap-1.5 text-sm">
        <i class="fa fa-arrow-left"></i>返回台风列表
      </button>
      <div class="flex items-center gap-3">
        <h1 class="text-2xl md:text-3xl font-bold">{{ info.typhoon_name }}</h1>
        <span :class="categoryBadgeClass(info.max_wind)"
          class="px-3 py-1 rounded-full text-sm font-semibold">{{ categoryLabel(info.max_wind) }}</span>
      </div>
      <p class="text-slate-300 mt-1 text-sm">
        {{ info.season }} 年 · {{ info.start_time }} ~ {{ info.end_time }} · {{ info.total_points }} 个观测点
        <span class="ml-3 inline-flex items-center gap-1 px-2.5 py-0.5 bg-white/10 rounded-full text-xs text-blue-200/70">
          <i class="fa fa-map-marker"></i>100°E–180°E · 0°–60°N
        </span>
      </p>
    </div>
  </div>

  <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ fmtWind(info.max_wind) === '-' ? '-' : info.max_wind }} <span class="text-sm text-slate-400">kts</span></div>
        <div class="text-xs text-slate-500 mt-1">最大风速</div>
      </div>
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ minPressureDisplay }} <span class="text-sm text-slate-400">hPa</span></div>
        <div class="text-xs text-slate-500 mt-1">{{ minPressureSource }}</div>
      </div>
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ trackPoints.length }}</div>
        <div class="text-xs text-slate-500 mt-1">路径点数</div>
      </div>
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ info.season }}</div>
        <div class="text-xs text-slate-500 mt-1">所属年份</div>
      </div>
    </div>

    <!-- 1. 台风路径地图 — 高德标准矢量底图 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-map-o text-indigo-500"></i>
        <span class="font-semibold text-slate-700">台风路径地图</span>
        <span class="text-xs text-slate-400 ml-auto">点击标记查看观测点信息</span>
      </div>
      <div class="relative">
        <div id="typhoon-map" style="height: 520px;"></div>
        <div v-if="mapLoading" class="absolute inset-0 bg-white/60 flex items-center justify-center">
          <div class="text-center">
            <div class="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p class="text-slate-500 text-sm mt-2">加载地图数据...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 1.5 空间密度分析 (PostGIS) -->
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
            <div class="text-xs text-slate-500 mt-1">邻近台风数</div>
          </div>
          <div class="text-center bg-slate-50 rounded-xl p-3">
            <div class="text-xl font-bold text-red-600">{{ spatialStats.avg_wind }} <span class="text-sm text-slate-400">kts</span></div>
            <div class="text-xs text-slate-500 mt-1">邻近平均风速</div>
          </div>
          <div class="text-center bg-slate-50 rounded-xl p-3">
            <div class="text-xl font-bold text-amber-600">{{ spatialStats.max_wind }} <span class="text-sm text-slate-400">kts</span></div>
            <div class="text-xs text-slate-500 mt-1">邻近最大风速</div>
          </div>
          <div class="text-center bg-slate-50 rounded-xl p-3">
            <div class="text-xl font-bold text-slate-800">{{ spatialStats.avg_pressure }} <span class="text-sm text-slate-400">hPa</span></div>
            <div class="text-xs text-slate-500 mt-1">邻近平均气压</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. 强度时序图 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-line-chart text-indigo-500"></i>
        <span class="font-semibold text-slate-700">强度时序变化</span>
        <span class="text-xs text-slate-400 ml-auto" id="chart-tooltip-text">鼠标悬停查看详情</span>
      </div>
      <div class="relative p-2">
        <canvas ref="chartCanvas" id="intensity-chart" style="width:100%;height:380px"></canvas>
      </div>
    </div>

    <!-- 3. AI 分析面板 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-magic text-purple-500"></i>
        <span class="font-semibold text-slate-700">AI 智能分析</span>
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
          <button @click="runAIAnalysis"
            :disabled="aiLoading"
            class="ml-auto px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl text-sm font-medium hover:shadow-lg hover:shadow-purple-600/20 transition-all disabled:opacity-60 flex items-center gap-2">
            <i :class="aiLoading ? 'fa fa-spinner fa-spin' : 'fa fa-play'"></i>
            {{ aiLoading ? 'AI 分析中...' : '开始分析' }}
          </button>
        </div>
        <div v-if="aiResult" class="bg-slate-50 rounded-xl p-5 border border-slate-100">
          <div v-if="aiCached" class="text-xs text-slate-400 mb-2 flex items-center gap-1">
            <i class="fa fa-database"></i> 缓存结果（首次生成后永久复用）
          </div>
          <div class="prose prose-sm max-w-none text-slate-700 whitespace-pre-wrap leading-relaxed">{{ aiResult }}</div>
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
          <p class="text-slate-500 text-sm mt-3">DeepSeek 正在分析台风数据，请稍候...</p>
        </div>
      </div>
    </div>

    <!-- 4. 出行建议 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-car text-green-500"></i>
        <span class="font-semibold text-slate-700">沿海城市出行建议</span>
      </div>
      <div class="p-5">
        <p class="text-sm text-slate-500 mb-3">基于台风数据为沿海城市的居民和旅客提供出行安全评估和建议。</p>
        <button @click="runTravelAdvice" :disabled="travelLoading"
          class="px-6 py-2.5 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-xl text-sm font-medium hover:shadow-lg hover:shadow-green-600/20 transition-all disabled:opacity-60 flex items-center gap-2">
          <i :class="travelLoading ? 'fa fa-spinner fa-spin' : 'fa fa-shield'"></i>
          {{ travelLoading ? '生成中...' : '生成出行建议' }}
        </button>
        <div v-if="travelResult" class="mt-4 bg-slate-50 rounded-xl p-5 border border-slate-100">
          <div class="prose prose-sm max-w-none text-slate-700 whitespace-pre-wrap leading-relaxed">{{ travelResult }}</div>
        </div>
        <div v-if="travelLoading" class="text-center py-6">
          <div class="inline-flex items-center gap-2 text-green-600">
            <div class="w-2 h-2 bg-green-600 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-green-600 rounded-full animate-bounce delay-150"></div>
            <div class="w-2 h-2 bg-green-600 rounded-full animate-bounce delay-300"></div>
          </div>
          <p class="text-slate-500 text-sm mt-3">正在生成出行建议...</p>
        </div>
      </div>
    </div>

  </div>
</div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import api from '../api'

const route = useRoute()
const typhoonId = route.params.id

const info = reactive({
  typhoon_id: '', typhoon_name: '', season: 0, max_wind: 0,
  min_pressure: 0, total_points: 0, start_time: '', end_time: '',
})
const trackPoints = ref([])
const spatialStats = ref(null)
const mapLoading = ref(true)

// ── 工具函数 ─────────────────────────────────────
function isMissingWind(w)  { return !w || w <= 0 }
function isMissingPress(p) { return !p || p >= 9999 }
function fmtWind(w)  { return isMissingWind(w)  ? '-' : w }
function fmtPressure(p) { return isMissingPress(p) ? '-' : p }
// 从路径点中计算实际观测到的最低气压（供卡片展示）
const minPressureDisplay = computed(() => {
  const obs = trackPoints.value.filter(p => !isMissingPress(p.min_pressure));
  if (obs.length === 0) {
    if (info.min_pressure && !isMissingPress(info.min_pressure)) return info.min_pressure;
    // 回退到汇总表中计算
    const tpObs = trackPoints.value.length > 0 ? Math.min(...trackPoints.value.map(p => p.min_pressure)) : 9999;
    return !isMissingPress(tpObs) ? tpObs : '-';
  }
  return Math.min(...obs.map(p => p.min_pressure));
})
const minPressureSource = computed(() => {
  const obs = trackPoints.value.filter(p => !isMissingPress(p.min_pressure))
  return obs.length > 0 ? '观测最低气压' : '汇总最低气压'
})
function fmtW(w)  { return isMissingWind(w)  ? '未观测' : w + ' kts' }
function fmtP(p)  { return isMissingPress(p) ? '未观测' : p + ' hPa' }
function categoryLabel(w) { if (isMissingWind(w)) return 'N/A'; return w>=130?'Super TY':w>=100?'强台风':w>=64?'台风':w>=34?'热带风暴':'热带低压' }
function categoryBadgeClass(w) { if (isMissingWind(w)) return 'bg-gray-100 text-gray-600'; return w>=130?'bg-red-100 text-red-700':w>=100?'bg-orange-100 text-orange-700':w>=64?'bg-amber-100 text-amber-700':w>=34?'bg-yellow-100 text-yellow-700':'bg-blue-100 text-blue-700' }
function windToColor(w) { if (isMissingWind(w)) return '#94a3b8'; return w>=130?'#ef4444':w>=100?'#f97316':w>=64?'#eab308':w>=34?'#22d3ee':'#60a5fa' }

// ── Leaflet 地图 + 高德标准矢量底图 ─────────────
let map = null, trackLayer = null, windLayer = null

function initMap() {
  if (map) return
  const gaodeVec = L.tileLayer(
    'https://webrd0{s}.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scale=1&style=8',
    { subdomains: ['1','2','3','4'], maxZoom: 10 }
  )
  map = L.map('typhoon-map', {
    center: [20, 140], zoom: 4, layers: [gaodeVec],
    zoomControl: true, minZoom: 3,
    maxBounds: [[-5, 90], [55, 190]], maxBoundsViscosity: 0.8,
  })
  trackLayer = L.featureGroup().addTo(map)
  windLayer = L.featureGroup().addTo(map)  // 持久化，不复建
  setTimeout(() => map.invalidateSize(), 200)
}

function renderTrack() {
  if (!map || trackPoints.value.length===0) return
  trackLayer.clearLayers()
  windLayer.clearLayers()

  const pts = trackPoints.value, lls = pts.map(p=>[p.latitude,p.longitude])

  L.polyline(lls, { color:'#60a5fa', weight:10, opacity:0.12, smoothFactor:1 }).addTo(trackLayer)
  for (let i=0; i<lls.length-1; i++)
    L.polyline([lls[i],lls[i+1]], { color:windToColor(pts[i].max_wind), weight:3.5, opacity:0.9, smoothFactor:1 }).addTo(trackLayer)

  // 起点 · 终点
  if (lls.length>0) L.circleMarker(lls[0], { radius:8, fillColor:'#22c55e', color:'#fff', weight:2, fillOpacity:1 }).addTo(trackLayer).bindPopup(`<b>起始点</b><br>${pts[0].datetime}<br>风速:${fmtW(pts[0].max_wind)}<br>气压:${fmtP(pts[0].min_pressure)}`)
  if (lls.length>1) L.circleMarker(lls[lls.length-1], { radius:8, fillColor:'#ef4444', color:'#fff', weight:2, fillOpacity:1 }).addTo(trackLayer).bindPopup(`<b>终点</b><br>${pts[pts.length-1].datetime}<br>风速:${fmtW(pts[pts.length-1].max_wind)}<br>气压:${fmtP(pts[pts.length-1].min_pressure)}`)

  // 强度峰值（仅在有有效风速的点中找）
  let mx = -1, mxWind = -1
  for (let i=0; i<pts.length; i++) {
    if (!isMissingWind(pts[i].max_wind) && pts[i].max_wind > mxWind) { mx=i; mxWind=pts[i].max_wind }
  }
  if (mx >= 0) {
    L.circleMarker(lls[mx], { radius:10, fillColor:'#fbbf24', color:'#fff', weight:2.5, fillOpacity:1 }).addTo(trackLayer).bindPopup(
      `<b>🏆 强度峰值</b><br>${pts[mx].datetime}<br>风速:${fmtW(pts[mx].max_wind)}<br>气压:${fmtP(pts[mx].min_pressure)}<br>等级:${pts[mx].storm_category||'N/A'}`
    )
  }

  // 风圈（取强度峰值点）
  if (mx >= 0 && pts[mx].wind_radius_7) {
    const r7=pts[mx].wind_radius_7, c=lls[mx], f=1/60, a7=(r7.ne+r7.se+r7.sw+r7.nw)/4
    if (a7>0) L.circle(c, { radius:a7*f*111320, color:'#fbbf24', weight:1.5, fillColor:'#fbbf24', fillOpacity:0.06, dashArray:'5,5', bubblingMouseEvents:false }).addTo(windLayer).bindPopup(`<b>七级风圈</b><br>NE:${r7.ne} SE:${r7.se}<br>SW:${r7.sw} NW:${r7.nw}<br>单位:海里`)
    const r10=pts[mx].wind_radius_10, a10=(r10.ne+r10.se+r10.sw+r10.nw)/4
    if (a10>0) L.circle(c, { radius:a10*f*111320, color:'#f97316', weight:1.5, fillColor:'#f97316', fillOpacity:0.04, dashArray:'5,5', bubblingMouseEvents:false }).addTo(windLayer).bindPopup(`<b>十级风圈</b><br>NE:${r10.ne} SE:${r10.se}<br>SW:${r10.sw} NW:${r10.nw}<br>单位:海里`)
  }

  // 采样观测点
  const st=Math.max(1,Math.floor(pts.length/12))
  for (let i=0; i<pts.length; i+=st) {
    const p=pts[i], cat=p.storm_category, r=cat==='C5'||cat==='C4'?14:cat?12:10
    L.circleMarker([p.latitude,p.longitude], { radius:r, fillColor:windToColor(p.max_wind), color:'#fff', weight:2.5, fillOpacity:0.9, bubblingMouseEvents:false }).addTo(trackLayer).bindPopup(
      `<b>${p.datetime}</b><br>风速:${fmtW(p.max_wind)} | 气压:${fmtP(p.min_pressure)}<br>等级:${p.storm_category||'N/A'}`
    )
  }

  trackLayer.bringToFront()
  map.fitBounds(L.latLngBounds(lls), { padding:[50,50] })
}

// ── Canvas 2D 强度时序图 ─────────────────────────
const chartCanvas=ref(null)
function drawChart() {
  const cv=chartCanvas.value; if(!cv||trackPoints.value.length===0){return}
  const ctx=cv.getContext('2d'), dpr=window.devicePixelRatio||1, rect=cv.getBoundingClientRect()
  cv.width=rect.width*dpr; cv.height=rect.height*dpr
  ctx.setTransform(dpr,0,0,dpr,0,0)
  const W=rect.width,H=rect.height; ctx.clearRect(0,0,W,H)
  const pts=trackPoints.value,n=pts.length; if(n<2) return
  const ws=pts.map(p=>isMissingWind(p.max_wind)?NaN:p.max_wind)
  const ps=pts.map(p=>isMissingPress(p.min_pressure)?NaN:p.min_pressure)
  const ts=pts.map(p=>new Date(p.datetime))

  // 风速和气压各自独立的有效范围
  const wrng=_validRange(ws), prng=_validRange(ps)
  const hasWind=!!wrng, hasPres=!!prng
  // 只要有一方有数据就渲染，两者都没有才退出
  if(!hasWind&&!hasPres){console.warn('[强度图表] 风速和气压均无有效观测数据');return}

  // X 轴时间范围取两方并集
  let lo=n-1,hi=0
  if(hasWind){lo=Math.min(lo,wrng.s);hi=Math.max(hi,wrng.e)}
  if(hasPres){lo=Math.min(lo,prng.s);hi=Math.max(hi,prng.e)}
  const vs=lo, ve=hi, vc=ve-vs; if(vc<1) return

  const pad={top:20,right:60,bottom:50,left:55},pw=W-pad.left-pad.right,ph=H-pad.top-pad.bottom

  // 风速 Y 轴范围（独立）
  let wmin=0,wmax=100
  if(hasWind){const wv=ws.slice(vs,ve+1).filter(v=>!isNaN(v));wmin=Math.max(0,Math.min(...wv)-(Math.max(...wv)-Math.min(...wv))*.15);wmax=Math.max(...wv)+(Math.max(...wv)-Math.min(...wv))*.15}

  // 气压 Y 轴范围（独立）
  let pmin=900,pmax=1020
  if(hasPres){const pv=ps.slice(vs,ve+1).filter(v=>!isNaN(v));pmin=Math.min(...pv)-(Math.max(...pv)-Math.min(...pv))*.1;pmax=Math.max(...pv)+(Math.max(...pv)-Math.min(...pv))*.1}

  const tX=i=>pad.left+((i-vs)/vc)*pw, tWY=v=>pad.top+ph-((v-wmin)/(wmax-wmin))*ph, tPY=v=>pad.top+ph-((v-pmin)/(pmax-pmin))*ph

  // 网格
  ctx.strokeStyle='#f1f5f9'; ctx.lineWidth=1
  for(let i=0;i<=5;i++){let y=pad.top+(ph/5)*i; ctx.beginPath(); ctx.moveTo(pad.left,y); ctx.lineTo(pad.left+pw,y); ctx.stroke()}
  // X 轴日期标签
  ctx.fillStyle='#94a3b8'; ctx.font='10px sans-serif'; ctx.textAlign='center'
  let xs=Math.max(1,Math.floor(vc/6))
  for(let i=vs;i<=ve;i+=xs){let d=ts[i]; ctx.fillText(`${d.getMonth()+1}/${d.getDate()}`,tX(i),H-8)}
  // Y 轴刻度（左：风速，右：气压）
  if(hasWind){ctx.textAlign='right'; for(let i=0;i<=4;i++){let v=wmin+((wmax-wmin)/4)*i; ctx.fillText(Math.round(v).toString(),pad.left-6,tWY(v)+4)}}
  if(hasPres){ctx.textAlign='left'; for(let i=0;i<=4;i++){let v=pmin+((pmax-pmin)/4)*i; ctx.fillText(Math.round(v).toString(),pad.left+pw+6,tPY(v)+4)}}

  // 图例（左下角）
  const lgx=pad.left+8, lgy=pad.top+ph+18
  if(hasWind){ctx.strokeStyle='#ef4444';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(lgx,lgy);ctx.lineTo(lgx+18,lgy);ctx.stroke();ctx.fillStyle='#334155';ctx.font='11px sans-serif';ctx.textAlign='left';ctx.fillText('最大风速(kts)',lgx+22,lgy+4)}
  const l2x=hasWind?lgx+130:lgx
  if(hasPres){ctx.strokeStyle='#3b82f6';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(l2x,lgy);ctx.lineTo(l2x+18,lgy);ctx.stroke();ctx.fillText('中心气压(hPa)',l2x+22,lgy+4)}

  // ── 气压折线 + 区域填充（独立绘制）──
  if(hasPres){
    ctx.beginPath(); let stt=false
    for(let i=vs;i<=ve;i++){if(isNaN(ps[i]))continue;let x=tX(i),y=tPY(ps[i]);stt?(ctx.lineTo(x,y)):(ctx.moveTo(x,y),stt=true)}
    if(stt){ctx.lineTo(tX(ve),pad.top+ph);ctx.lineTo(tX(vs),pad.top+ph);ctx.closePath();let g=ctx.createLinearGradient(0,pad.top,0,pad.top+ph);g.addColorStop(0,'rgba(59,130,246,.2)');g.addColorStop(1,'rgba(59,130,246,.02)');ctx.fillStyle=g;ctx.fill()}
    ctx.beginPath(); stt=false
    for(let i=vs;i<=ve;i++){if(isNaN(ps[i]))continue;let x=tX(i),y=tPY(ps[i]);stt?(ctx.lineTo(x,y)):(ctx.moveTo(x,y),stt=true)}
    ctx.strokeStyle='#3b82f6';ctx.lineWidth=2;ctx.stroke()
  }

  // ── 风速折线 + 区域填充（独立绘制）──
  if(hasWind){
    ctx.beginPath(); let fst=true,lx2=0
    for(let i=vs;i<=ve;i++){if(isNaN(ws[i]))continue;let x=tX(i),y=tWY(ws[i]);if(fst){ctx.moveTo(x,pad.top+ph);ctx.lineTo(x,y);fst=false}else ctx.lineTo(x,y);lx2=x}
    if(!fst){ctx.lineTo(lx2,pad.top+ph);ctx.closePath();let wg=ctx.createLinearGradient(0,pad.top,0,pad.top+ph);wg.addColorStop(0,'rgba(239,68,68,.25)');wg.addColorStop(1,'rgba(239,68,68,.03)');ctx.fillStyle=wg;ctx.fill()}
    ctx.beginPath(); fst=true
    for(let i=vs;i<=ve;i++){if(isNaN(ws[i]))continue;let x=tX(i),y=tWY(ws[i]);fst?(ctx.moveTo(x,y),fst=false):ctx.lineTo(x,y)}
    ctx.strokeStyle='#ef4444';ctx.lineWidth=2;ctx.stroke()
  }

  // 无数据提示横幅
  if(!hasPres||!hasWind){
    let msg=''
    if(!hasWind&&!hasPres) msg='风速和气压均无有效观测数据'
    else if(!hasWind) msg='风速数据缺失，仅显示气压'
    else msg='气压数据缺失，仅显示风速'
    ctx.fillStyle='rgba(0,0,0,.06)'; ctx.font='bold 14px sans-serif'; ctx.textAlign='center'
    ctx.fillText(msg, pad.left+pw/2, pad.top+ph/2)
  }

  // 鼠标交互
  cv.onmousemove=e=>{
    let mx=e.offsetX,idx=Math.round(vs+((mx-pad.left)/pw)*vc)
    if(idx<vs||idx>ve) return
    let tip=document.getElementById('chart-tooltip-text')
    if(tip) tip.textContent=`${ts[idx].toLocaleString('zh-CN',{month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'})} | 风速 ${isMissingWind(ws[idx])?'未观测':ws[idx]+'kts'} | 气压 ${isMissingPress(ps[idx])?'未观测':ps[idx]+'hPa'}`
    drawChart()
    let cx=tX(idx); ctx.beginPath(); ctx.moveTo(cx,pad.top); ctx.lineTo(cx,pad.top+ph); ctx.strokeStyle='#94a3b8'; ctx.lineWidth=1; ctx.setLineDash([4,4]); ctx.stroke(); ctx.setLineDash([])
  }
  cv.onmouseleave=()=>{let tip=document.getElementById('chart-tooltip-text'); if(tip) tip.textContent='鼠标悬停查看详情'; drawChart()}
}

// 辅助：找数组中有效数值的首尾索引
function _validRange(arr){
  let s=0,e=arr.length-1; while(s<e&&isNaN(arr[s]))s++; while(e>s&&isNaN(arr[e]))e--
  return s<e && arr.slice(s,e+1).filter(v=>!isNaN(v)).length>=2 ? {s,e} : null
}
let cro=null

// ── AI ──────────────────────────────────────────
const analysisTypes=[{value:'trend',label:'路径趋势',icon:'fa fa-signal'},{value:'compare',label:'历史对比',icon:'fa fa-exchange'},{value:'impact',label:'影响评估',icon:'fa fa-exclamation-triangle'}]
const selectedAnalysis=ref('trend'),aiResult=ref(''),aiCached=ref(false),aiLoading=ref(false)
async function runAIAnalysis(){aiResult.value=''; aiCached.value=false; aiLoading.value=true; try{let{data:r}=await api.post('/api/typhoon/ai_analysis',{typhoon_id:typhoonId,analysis_type:selectedAnalysis.value},{timeout:90000}); if(r.code===200){aiResult.value=r.data.content; aiCached.value=!!r.data.cached}else aiResult.value='❌ '+r.message}catch(e){aiResult.value='❌ AI 分析请求失败'} finally{aiLoading.value=false}}
const travelResult=ref(''),travelLoading=ref(false)
async function runTravelAdvice(){travelResult.value=''; travelLoading.value=true; try{let{data:r}=await api.post('/api/typhoon/ai_analysis',{typhoon_id:typhoonId,analysis_type:'travel'},{timeout:90000}); if(r.code===200) travelResult.value=r.data.content; else travelResult.value='❌ '+r.message}catch(e){travelResult.value='❌ 出行建议生成失败'} finally{travelLoading.value=false}}

async function fetchData(){try{let[a,b]=await Promise.all([api.get(`/api/typhoon/${typhoonId}`),api.get(`/api/typhoon/${typhoonId}/track`)]); if(a.data.code===200){Object.assign(info,a.data.data); spatialStats.value = a.data.data.spatial_stats || null}; if(b.data.code===200) trackPoints.value=b.data.data.points}catch(e){console.error(e)}}
onMounted(async()=>{await fetchData(); mapLoading.value=false; await nextTick(); initMap(); renderTrack(); drawChart(); cro=new ResizeObserver(()=>drawChart()); cro.observe(chartCanvas.value?.parentElement)})
onUnmounted(()=>{map?.remove(); map=null; cro?.disconnect()})
</script>

<style>
.delay-150{animation-delay:.15s}
.delay-300{animation-delay:.3s}
#typhoon-map .leaflet-container{background:#e8e8e8}
#typhoon-map .leaflet-control-zoom a{background:#1e293b;color:#e2e8f0;border-color:#334155}
#typhoon-map .leaflet-control-attribution{background:rgba(15,23,42,.75);color:#64748b;font-size:10px}
#typhoon-map .leaflet-popup-content-wrapper{background:rgba(30,41,59,.94);color:#e2e8f0;border-radius:12px;backdrop-filter:blur(8px)}
#typhoon-map .leaflet-popup-tip{background:rgba(30,41,59,.94)}
</style>
