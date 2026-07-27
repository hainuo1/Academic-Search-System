<template>
<div class="min-h-screen bg-slate-50">

  <div class="bg-gradient-to-r from-slate-800 via-indigo-900 to-blue-950 text-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6">
      <button @click="$router.push('/earthquake')"
        class="text-slate-300 hover:text-white transition-colors mb-3 flex items-center gap-1.5 text-sm">
        <i class="fa fa-arrow-left"></i>返回地震列表
      </button>
      <div class="flex items-center gap-3">
        <h1 class="text-2xl md:text-3xl font-bold">{{ detail.place ? detail.place.substring(0,60) : detail.event_id }}</h1>
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

    <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
      <div v-for="card in topCards" :key="card.label" class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm p-4 text-center">
        <div class="text-2xl font-bold text-slate-800">{{ card.value }}</div>
        <div class="text-xs text-slate-500 mt-1">{{ card.label }}</div>
      </div>
    </div>

    <!-- 空间密度分析 (PostGIS) -->
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
            <div class="text-xs text-slate-500 mt-1">邻近地震数</div>
          </div>
          <div class="text-center bg-slate-50 rounded-xl p-3">
            <div class="text-xl font-bold text-red-600">{{ spatialStats.avg_magnitude }}</div>
            <div class="text-xs text-slate-500 mt-1">邻近平均震级</div>
          </div>
          <div class="text-center bg-slate-50 rounded-xl p-3">
            <div class="text-xl font-bold text-amber-600">{{ spatialStats.max_magnitude }}</div>
            <div class="text-xs text-slate-500 mt-1">邻近最大震级</div>
          </div>
          <div class="text-center bg-slate-50 rounded-xl p-3">
            <div class="text-xl font-bold text-slate-800">{{ spatialStats.avg_depth }} <span class="text-sm text-slate-400">km</span></div>
            <div class="text-xs text-slate-500 mt-1">邻近平均深度</div>
          </div>
          <div class="text-center bg-slate-50 rounded-xl p-3">
            <div class="text-xl font-bold text-red-500">{{ spatialStats.strong_count }}</div>
            <div class="text-xs text-slate-500 mt-1">M≥6 强震</div>
          </div>
          <div class="text-center bg-slate-50 rounded-xl p-3">
            <div class="text-xl font-bold text-red-700">{{ spatialStats.major_count }}</div>
            <div class="text-xs text-slate-500 mt-1">M≥7 大震</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 震中位置地图 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-map-o text-amber-500"></i>
        <span class="font-semibold text-slate-700">震中位置</span>
      </div>
      <div class="relative">
        <div id="earthquake-map" style="height:480px"></div>
        <div v-if="mapLoading" class="absolute inset-0 bg-white/60 flex items-center justify-center">
          <div class="text-center">
            <div class="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p class="text-slate-500 text-sm mt-2">加载中...</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 四维属性柱状图 -->
    <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-100 shadow-sm mb-6 overflow-hidden">
      <div class="px-5 py-4 border-b border-slate-100 flex items-center gap-2">
        <i class="fa fa-bar-chart text-amber-500"></i>
        <span class="font-semibold text-slate-700">事件属性对比柱状图</span>
        <span class="text-xs text-slate-400 ml-auto">当前事件 vs 区域历史均值（±3°范围）</span>
      </div>
      <div class="relative p-2">
        <canvas ref="barCanvas" style="width:100%;height:380px"></canvas>
      </div>
    </div>

    <!-- 区域地震活动趋势 -->
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

    <!-- AI 分析 -->
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
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import api from '../api';

const route = useRoute();
const eventId = route.params.id;

const detail = reactive({});
const nearby = ref([]);
const mapLoading = ref(true);
const spatialStats = ref(null);

const trendCanvas = ref(null);
const barCanvas = ref(null);

let map = null, marker = null, cro = null;

const topCards = computed(function() {
  return [
    { label: '震级（M）', value: (detail.magnitude||0).toFixed(1) },
    { label: '震源深度（km）', value: detail.depth || '-' },
    { label: '定位台站数', value: detail.nst || '-' },
  ];
});

function magBadgeClass(m) {
  if (m >= 7) return 'bg-red-100 text-red-700';
  if (m >= 6) return 'bg-orange-100 text-orange-700';
  if (m >= 5) return 'bg-amber-100 text-amber-700';
  return 'bg-blue-100 text-blue-700';
}

function initMap() {
  if (map) return;
  map = L.map('earthquake-map', {
    center: [35, 104], zoom: 5, minZoom: 4,
    maxBounds: [[-90, -180], [90, 180]], maxBoundsViscosity: 0.8,
    layers: [L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scale=1&style=8', { subdomains: ['1','2','3','4'], maxZoom: 10 })]
  });
  setTimeout(function() { map.invalidateSize(); }, 200);
}

function renderMap() {
  if (!map || !detail.latitude) return;
  if (marker) map.removeLayer(marker);
  var ll = [detail.latitude, detail.longitude];
  var r = Math.max(6, (detail.magnitude||4)*5);
  var c = detail.magnitude>=7?'#ef4444':detail.magnitude>=6?'#f97316':detail.magnitude>=5?'#eab308':'#3b82f6';
  marker = L.circleMarker(ll, { radius:r, fillColor:c, color:'#fff', weight:2, fillOpacity:0.8 })
    .addTo(map).bindPopup('<b>'+detail.place+'</b><br>'+detail.datetime+'<br>M'+(detail.magnitude||0).toFixed(1)+' · '+detail.depth+'km').openPopup();
  L.circle(ll, { radius:Math.min((detail.depth||10)*1500,300000), color:'#f59e0b', weight:1, fillColor:'#f59e0b', fillOpacity:0.06, dashArray:'4,4', bubblingMouseEvents:false }).addTo(map);
  map.setView(ll, 7);
}

function drawTrend() {
  var cv = trendCanvas.value;
  if (!cv || nearby.value.length === 0) return;
  var ctx = cv.getContext('2d');
  var dpr = window.devicePixelRatio || 1;
  var rect = cv.getBoundingClientRect();
  cv.width = rect.width * dpr;
  cv.height = rect.height * dpr;
  ctx.scale(dpr, dpr);
  var W = rect.width, H = rect.height;
  ctx.clearRect(0, 0, W, H);

  var data = nearby.value.slice();
  data.push({datetime: detail.datetime, magnitude: detail.magnitude, he: detail.horizontal_error});
  data.sort(function(a, b) { return new Date(a.datetime) - new Date(b.datetime); });
  var n = data.length;
  if (n < 2) return;

  // X 轴使用均匀的索引映射（每个数据点等间距）
  var pad = {top: 20, right: 60, bottom: 55, left: 55};
  var pw = W - pad.left - pad.right, ph = H - pad.top - pad.bottom;
  var mags = data.map(function(d) { return d.magnitude || 0; });
  var hes = data.map(function(d) { return d.he || 0; });
  var mMin = Math.min.apply(null, mags);
  var mMax = Math.max.apply(null, mags);
  var heMax = Math.max.apply(null, hes.concat([0.1]));
  var myMin = Math.max(0, mMin - 0.5), myMax = mMax + 1;
  // 均匀分布每个点到 X 轴上
  var tX = function(i) { return pad.left + (i / (n - 1)) * pw; };
  var tY = function(v) { return pad.top + ph - ((v - myMin) / (myMax - myMin)) * ph; };

  ctx.strokeStyle = '#f1f5f9'; ctx.lineWidth = 1;
  for (var i = 0; i <= 5; i++) {
    var y = pad.top + (ph / 5) * i;
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(pad.left + pw, y); ctx.stroke();
  }

  // X 轴日期标签 —— 按年份+月份均匀间隔标注，确保每年都显示
  ctx.fillStyle = '#94a3b8'; ctx.font = '9px sans-serif'; ctx.textAlign = 'center';
  var years = data.map(function(d) { return new Date(d.datetime).getFullYear(); });
  var minYear = years[0], maxYear = years[n - 1];
  var yearSpan = maxYear - minYear;
  // 利用数据点的年份信息，找到每年第一个数据点的位置标注年份
  var labeled = {}; // 避免同一年重复标
  var yearLabels = [];
  var lastSeenYear = -1;
  for (var i = 0; i < n; i++) {
    var d = new Date(data[i].datetime);
    var yr = d.getFullYear();
    if (yr !== lastSeenYear && !labeled[yr]) {
      yearLabels.push({ i: i, label: String(yr) });
      labeled[yr] = true;
      lastSeenYear = yr;
    }
  }

  // 如果年份标签太少（≤6个），额外在各年年中位置加注月份短标
  if (yearLabels.length <= 6 && yearLabels.length > 0) {
    var extraLabels = [];
    for (var yi = 0; yi < yearLabels.length; yi++) {
      var yStart = yearLabels[yi].i;
      var yEnd = (yi + 1 < yearLabels.length) ? yearLabels[yi + 1].i : n - 1;
      if (yEnd - yStart > 2) {
        var mid = Math.floor((yStart + yEnd) / 2);
        var md = new Date(data[mid].datetime);
        extraLabels.push({ i: mid, label: (md.getMonth() + 1) + '/' + md.getDate(), isSub: true });
        // 再加一个 1/3 和 2/3 位置的点
        var q1 = Math.floor(yStart + (yEnd - yStart) / 3);
        if (q1 > yStart + 2) {
          var q1d = new Date(data[q1].datetime);
          extraLabels.push({ i: q1, label: (q1d.getMonth() + 1) + '/' + q1d.getDate(), isSub: true });
        }
        var q2 = Math.floor(yStart + (yEnd - yStart) * 2 / 3);
        if (q2 < yEnd - 2) {
          var q2d = new Date(data[q2].datetime);
          extraLabels.push({ i: q2, label: (q2d.getMonth() + 1) + '/' + q2d.getDate(), isSub: true });
        }
      }
    }
    // 合并标签，按索引排序
    var allLabels = yearLabels.concat(extraLabels);
    allLabels.sort(function(a, b) { return a.i - b.i; });
    // 去重相近的标签（间隔小于 n/30 的跳过子标签）
    var finalLabels = [];
    var minGap = Math.max(1, Math.floor(n / 20));
    for (var li = 0; li < allLabels.length; li++) {
      if (finalLabels.length === 0) { finalLabels.push(allLabels[li]); continue; }
      if (allLabels[li].i - finalLabels[finalLabels.length - 1].i < minGap && allLabels[li].isSub) continue;
      finalLabels.push(allLabels[li]);
    }
    // 渲染
    for (var li = 0; li < finalLabels.length; li++) {
      var lb = finalLabels[li];
      ctx.font = lb.isSub ? '8px sans-serif' : 'bold 10px sans-serif';
      ctx.fillStyle = lb.isSub ? '#94a3b8' : '#475569';
      ctx.fillText(lb.label, tX(lb.i), H - 8);
    }
  } else {
    // 年份多时直接标注每年
    for (var li = 0; li < yearLabels.length; li++) {
      ctx.font = 'bold 10px sans-serif';
      ctx.fillStyle = '#475569';
      ctx.fillText(yearLabels[li].label, tX(yearLabels[li].i), H - 8);
    }
  }
  ctx.textAlign = 'right';
  for (var i = 0; i <= 4; i++) {
    var v = myMin + ((myMax - myMin) / 4) * i;
    ctx.fillText(v.toFixed(1), pad.left - 6, tY(v) + 4);
  }

  ctx.beginPath();
  ctx.moveTo(tX(0), pad.top + ph);
  for (var i = 0; i < n; i++) ctx.lineTo(tX(i), tY(mags[i]));
  ctx.lineTo(tX(n - 1), pad.top + ph); ctx.closePath();
  var g = ctx.createLinearGradient(0, pad.top, 0, pad.top + ph);
  g.addColorStop(0, 'rgba(239,68,68,.18)'); g.addColorStop(1, 'rgba(239,68,68,.02)');
  ctx.fillStyle = g; ctx.fill();

  ctx.beginPath();
  ctx.moveTo(tX(0), tY(mags[0]));
  for (var i = 1; i < n; i++) ctx.lineTo(tX(i), tY(mags[i]));
  ctx.strokeStyle = '#ef4444'; ctx.lineWidth = 2; ctx.stroke();

  for (var i = 0; i < n; i++) {
    var r = 2.5 + (hes[i] / heMax) * 7;
    var isCur = data[i].datetime === detail.datetime;
    ctx.beginPath();
    ctx.arc(tX(i), tY(mags[i]), isCur ? r + 3 : r, 0, Math.PI * 2);
    ctx.fillStyle = isCur ? '#fbbf24' : '#ef4444';
    ctx.strokeStyle = isCur ? '#fff' : 'transparent';
    ctx.lineWidth = isCur ? 2 : 0;
    ctx.fill(); ctx.stroke();
  }

  ctx.fillStyle = '#334155'; ctx.font = '10px sans-serif'; ctx.textAlign = 'left';
  ctx.fillText('散点大小 = 水平误差 · 金色 = 当前事件', pad.left + 8, pad.top + ph + 14);
  ctx.fillText('单位: 震级(M)', pad.left + 8, pad.top + ph + 26);

  cv.onmousemove = function(e) {
    var mx = e.offsetX;
    var best = 0, bestDist = Infinity;
    for (var i = 0; i < n; i++) {
      var dist = Math.abs(tX(i) - mx);
      if (dist < bestDist) { bestDist = dist; best = i; }
    }
    if (best < 0 || best >= n) return;
    var tip = document.getElementById('eq-trend-tooltip');
    if (tip) tip.textContent = data[best].datetime + ' | M' + mags[best].toFixed(1) + ' | 水平误差' + hes[best].toFixed(1) + 'km';
  };
  cv.onmouseleave = function() {
    var tip = document.getElementById('eq-trend-tooltip');
    if (tip) tip.textContent = '鼠标悬停查看详情';
  };
}

function drawBarChart() {
  var cv = barCanvas.value;
  if (!cv) return;
  var ctx = cv.getContext('2d');
  var dpr = window.devicePixelRatio || 1;
  var rect = cv.getBoundingClientRect();
  if (rect.width === 0 || rect.height === 0) return;
  cv.width = rect.width * dpr; cv.height = rect.height * dpr;
  ctx.scale(dpr, dpr);
  var W = rect.width, H = rect.height;
  ctx.clearRect(0, 0, W, H);

  var allV = nearby.value.length > 0 ? nearby.value : [];
  // 安全均值：排除 null/undefined
  var safeAvg = function(key) {
    var vals = allV.map(function(d) { return d[key]; }).filter(function(v) { return v != null; });
    return vals.length ? vals.reduce(function(a, b) { return a + b; }, 0) / vals.length : null;
  };

  var curVals = [
    { label: '震级(M)',      key: 'magnitude',        cmax: 10 },
    { label: '震源深度(km)', key: 'depth',            cmax: 300 },
    { label: '定位台站数',   key: 'nst',              cmax: 300 },
    { label: '水平误差(km)', key: 'horizontal_error', cmax: 20 },
  ];

  // 填充当前值和区域均值，缺失时为 null
  for (var i = 0; i < curVals.length; i++) {
    var k = curVals[i].key;
    curVals[i].cur = detail[k] != null ? detail[k] : null;
    curVals[i].avg = safeAvg(k);
  }

  var n = curVals.length;
  var pad = {top: 55, right: 40, bottom: 70, left: 55};
  var pw = W - pad.left - pad.right, ph = H - pad.top - pad.bottom;
  var groupW = pw / n;
  var barW = Math.min(groupW * 0.28, 48);
  var gap = 10, pairW = barW * 2 + gap;

  ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, W, H);

  ctx.strokeStyle = '#f1f5f9'; ctx.lineWidth = 1;
  for (var i = 0; i <= 5; i++) {
    var y = pad.top + (ph / 5) * i;
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(pad.left + pw, y); ctx.stroke();
  }
  ctx.fillStyle = '#64748b'; ctx.font = '11px sans-serif'; ctx.textAlign = 'right';
  for (var i = 0; i <= 5; i++) {
    ctx.fillText(Math.round((5 - i) / 5 * 10).toString(), pad.left - 8, pad.top + (ph / 5) * i + 4);
  }

  var legY = pad.top - 33;
  ctx.fillStyle = '#ef4444'; ctx.fillRect(pad.left + 8, legY, 18, 12);
  ctx.fillStyle = '#1e293b'; ctx.font = '11px sans-serif'; ctx.textAlign = 'left';
  ctx.fillText('当前事件', pad.left + 30, legY + 10);
  ctx.fillStyle = '#94a3b8'; ctx.fillRect(pad.left + 120, legY, 18, 12);
  ctx.fillText('区域均值', pad.left + 142, legY + 10);

  for (var i = 0; i < n; i++) {
    var centerX = pad.left + groupW * i + groupW / 2;
    var d = curVals[i];
    var curNorm = d.cur != null ? Math.min(d.cur / d.cmax, 1) : 0;
    var avgNorm = d.avg != null ? Math.min(d.avg / d.cmax, 1) : 0;
    var curH = d.cur != null ? Math.max(3, curNorm * ph) : 0;
    var avgH = d.avg != null ? Math.max(2, avgNorm * ph) : 0;
    var curX = centerX - pairW / 2;
    var avgX = centerX - pairW / 2 + barW + gap;

    // 区域均值柱（灰色）
    if (d.avg != null) {
      ctx.fillStyle = '#94a3b8';
      ctx.fillRect(avgX, pad.top + ph - avgH, barW, avgH);
    } else {
      // 缺失时画虚线框
      ctx.strokeStyle = '#cbd5e1'; ctx.lineWidth = 1; ctx.setLineDash([4, 4]);
      ctx.strokeRect(avgX, pad.top + ph - 20, barW, 20); ctx.setLineDash([]);
    }

    // 当前事件柱（红色）
    if (d.cur != null) {
      ctx.fillStyle = '#ef4444';
      ctx.fillRect(curX, pad.top + ph - curH, barW, curH);
    } else {
      // 缺失时画虚线框
      ctx.strokeStyle = '#fecaca'; ctx.lineWidth = 1; ctx.setLineDash([4, 4]);
      ctx.strokeRect(curX, pad.top + ph - 20, barW, 20); ctx.setLineDash([]);
    }

    // 数值标签
    ctx.font = 'bold 11px sans-serif'; ctx.textAlign = 'center';
    if (d.cur != null) {
      ctx.fillStyle = '#b91c1c';
      ctx.fillText(d.cur.toFixed(1), curX + barW / 2, pad.top + ph - curH - 6);
    } else {
      ctx.fillStyle = '#94a3b8';
      ctx.fillText('-', curX + barW / 2, pad.top + ph - 24);
    }
    if (d.avg != null) {
      ctx.fillStyle = '#64748b';
      if (avgH > 16) ctx.fillText(d.avg.toFixed(1), avgX + barW / 2, pad.top + ph - avgH + 16);
      else ctx.fillText(d.avg.toFixed(1), avgX + barW / 2, pad.top + ph - avgH - 6);
    } else {
      ctx.fillStyle = '#cbd5e1';
      ctx.fillText('-', avgX + barW / 2, pad.top + ph - 24);
    }

    ctx.fillStyle = '#334155'; ctx.font = 'bold 12px sans-serif';
    ctx.fillText(d.label, centerX, H - 10);
  }
}

var analysisTypes = [
  { value: 'trend', label: '活动趋势' },
  { value: 'risk',  label: '风险评估' },
  { value: 'impact', label: '影响分析' },
];
var selectedAnalysis = ref('trend');
var aiResult = ref('');
var aiCached = ref(false);
var aiLoading = ref(false);

async function runAIAnalysis() {
  aiResult.value = ''; aiCached.value = false; aiLoading.value = true;
  try {
    var res = await api.post('/api/earthquake/ai_analysis', {event_id: eventId, analysis_type: selectedAnalysis.value}, {timeout: 90000});
    if (res.data.code === 200) {
      aiResult.value = res.data.data.content;
      aiCached.value = !!res.data.data.cached;
    } else {
      aiResult.value = '❌ ' + res.data.message;
    }
  } catch (e) {
    aiResult.value = '❌ 请求失败';
  } finally {
    aiLoading.value = false;
  }
}

async function fetchData() {
  try {
    var res = await api.get('/api/earthquake/' + eventId);
    if (res.data.code === 200) {
      Object.assign(detail, res.data.data.detail);
      nearby.value = res.data.data.nearby;
      spatialStats.value = res.data.data.spatial_stats || null;
    }
  } catch (e) {
    console.error(e);
  }
}

onMounted(async function() {
  await fetchData();
  mapLoading.value = false;
  await nextTick();
  initMap();
  renderMap();
  drawBarChart();
  drawTrend();
  cro = new ResizeObserver(function() {
    drawBarChart();
    drawTrend();
  });
  var el = trendCanvas.value ? trendCanvas.value.parentElement : null;
  if (el) cro.observe(el);
  var el2 = barCanvas.value ? barCanvas.value.parentElement : null;
  if (el2) cro.observe(el2);
});

onUnmounted(function() {
  if (map) { map.remove(); map = null; }
  if (cro) { cro.disconnect(); }
});
</script>

<style>
.delay-150{animation-delay:.15s}.delay-300{animation-delay:.3s}
#earthquake-map .leaflet-container{background:#e8e8e8}
#earthquake-map .leaflet-control-zoom a{background:#1e293b;color:#e2e8f0;border-color:#334155}
#earthquake-map .leaflet-control-attribution{background:rgba(15,23,42,.75);color:#64748b;font-size:10px}
#earthquake-map .leaflet-popup-content-wrapper{background:rgba(30,41,59,.94);color:#e2e8f0;border-radius:12px}
#earthquake-map .leaflet-popup-tip{background:rgba(30,41,59,.94)}
</style>