<template>
<div>
  <section class="relative min-h-screen flex items-center justify-center overflow-hidden">
    <div class="absolute inset-0 bg-gradient-to-b from-slate-950 via-blue-950 to-indigo-950">
      <div class="absolute inset-0 opacity-20" style="background:radial-gradient(ellipse 80% 60% at 20% 40%, rgba(56,189,248,0.3) 0%, transparent 60%),radial-gradient(ellipse 60% 50% at 70% 30%, rgba(99,102,241,0.25) 0%, transparent 60%),radial-gradient(ellipse 70% 40% at 50% 70%, rgba(34,211,238,0.2) 0%, transparent 50%),radial-gradient(ellipse 50% 30% at 85% 60%, rgba(148,163,184,0.15) 0%, transparent 50%)"></div>
      <div class="absolute inset-0 opacity-15" style="background-image:radial-gradient(1px 1px at 10% 15%,#e2e8f0,transparent),radial-gradient(1px 1px at 25% 45%,#e2e8f0,transparent),radial-gradient(1px 1px at 40% 25%,#e2e8f0,transparent),radial-gradient(1px 1px at 55% 55%,#e2e8f0,transparent),radial-gradient(1px 1px at 70% 35%,#e2e8f0,transparent),radial-gradient(1px 1px at 85% 65%,#e2e8f0,transparent),radial-gradient(1px 1px at 15% 75%,#e2e8f0,transparent),radial-gradient(1px 1px at 60% 80%,#e2e8f0,transparent),radial-gradient(1px 1px at 90% 15%,#e2e8f0,transparent),radial-gradient(1px 1px at 35% 85%,#e2e8f0,transparent)"></div>
      <div class="absolute top-0 left-1/4 w-[500px] h-[300px] bg-cyan-500/10 rounded-full blur-[100px] animate-float-slow"></div>
      <div class="absolute bottom-0 right-1/4 w-[400px] h-[250px] bg-indigo-500/10 rounded-full blur-[100px] animate-float-delay"></div>
    </div>
    <div class="relative z-10 max-w-3xl mx-auto px-6 text-center text-white">
      <div class="inline-flex items-center gap-2 px-5 py-2 mb-10 bg-white/8 backdrop-blur-md rounded-full text-sm font-light tracking-wide border border-white/10 text-blue-200/80"><span class="text-cyan-400/70">◆</span> 南京农业大学 · 气象科学研究数据平台 v6.1</div>
      <div class="mb-8"><div class="inline-flex items-center justify-center w-24 h-24 rounded-full bg-white/5 backdrop-blur-sm border border-white/10 shadow-[0_0_60px_rgba(34,211,238,0.15)]"><i class="fa fa-globe text-4xl text-cyan-300/80"></i></div></div>
      <h1 class="text-4xl md:text-5xl lg:text-6xl font-light mb-6 leading-tight tracking-wide"><span class="bg-gradient-to-r from-cyan-200 via-blue-200 to-indigo-200 bg-clip-text text-transparent">气象科学研究数据平台</span></h1>
      <p class="text-lg md:text-xl text-blue-200/60 mb-4 font-light tracking-wider">热带气旋 · 龙卷风 · 地震监测 · 学术文献检索</p>
      <p class="text-sm md:text-base text-blue-200/30 max-w-xl mx-auto mb-12 leading-relaxed">面向大气科学研究的综合性数据平台——集成多源自然灾害历史观测数据，搭载 DeepSeek 大语言模型智能分析引擎，同步提供学术文献的多维度检索与知识管理服务。</p>
      <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
        <router-link to="/login" class="px-10 py-3.5 bg-white/90 text-indigo-800 font-medium rounded-2xl hover:bg-white hover:shadow-2xl hover:shadow-cyan-500/20 transition-all duration-500 transform hover:-translate-y-0.5 text-base">登录平台</router-link>
        <router-link to="/register" class="px-10 py-3.5 bg-white/8 text-white/80 font-medium rounded-2xl border border-white/15 hover:bg-white/15 hover:text-white hover:border-white/25 transition-all duration-500 text-base">注册账号</router-link>
      </div>
      <p class="text-blue-200/20 text-xs mt-8">已有账号可直接登录，新用户请注册后使用</p>
    </div>
    <div class="absolute bottom-12 left-1/2 -translate-x-1/2 z-10 text-white/15 animate-bounce"><i class="fa fa-chevron-down"></i></div>
  </section>
  <section class="bg-white py-24">
    <div class="max-w-5xl mx-auto px-6">
      <div class="text-center mb-16"><p class="text-xs text-slate-400 tracking-[0.2em] uppercase mb-3 font-medium">system overview</p><h2 class="text-2xl md:text-3xl font-light text-slate-800 mb-3">四大功能模块</h2><p class="text-slate-400 text-sm max-w-md mx-auto">三大自然灾害观测数据板块与学术文献检索管理并行</p><div class="w-12 h-px bg-gradient-to-r from-cyan-400 to-indigo-500 mx-auto mt-6"></div></div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="group bg-slate-50 rounded-3xl p-6 md:p-8 transition-all duration-500 hover:shadow-2xl hover:shadow-cyan-500/5 border border-slate-100 hover:border-cyan-200"><div class="flex items-start gap-4 mb-5"><div class="w-13 h-13 rounded-2xl bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/15 flex-shrink-0"><i class="fa fa-dot-circle-o text-white text-xl"></i></div><div><h3 class="text-base font-semibold text-slate-800 mb-0.5">热带气旋</h3><p class="text-[11px] text-slate-400">Typhoon Analysis</p></div></div><p class="text-xs text-slate-500 leading-relaxed">基于 IBTrACS 国际台风数据集，提供太平洋区域热带气旋历史路径可视化、强度时序分析、风场结构展示，结合 DeepSeek AI 辅助科学解读。</p></div>
        <div class="group bg-slate-50 rounded-3xl p-6 md:p-8 transition-all duration-500 hover:shadow-2xl hover:shadow-teal-500/5 border border-slate-100 hover:border-teal-200"><div class="flex items-start gap-4 mb-5"><div class="w-13 h-13 rounded-2xl bg-gradient-to-br from-teal-400 to-emerald-500 flex items-center justify-center shadow-lg shadow-teal-500/15 flex-shrink-0"><i class="fa fa-cloud text-white text-xl"></i></div><div><h3 class="text-base font-semibold text-slate-800 mb-0.5">龙卷风</h3><p class="text-[11px] text-slate-400">Tornado Analysis</p></div></div><p class="text-xs text-slate-500 leading-relaxed">覆盖美国全境龙卷风历史事件数据，提供 EF 等级强度分析、地理空间分布可视化、频次统计趋势，DeepSeek AI 成因解读与趋势研判。</p></div>
        <div class="group bg-slate-50 rounded-3xl p-6 md:p-8 transition-all duration-500 hover:shadow-2xl hover:shadow-amber-500/5 border border-slate-100 hover:border-amber-200"><div class="flex items-start gap-4 mb-5"><div class="w-13 h-13 rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-lg shadow-amber-500/15 flex-shrink-0"><i class="fa fa-warning text-white text-xl"></i></div><div><h3 class="text-base font-semibold text-slate-800 mb-0.5">地震监测</h3><p class="text-[11px] text-slate-400">Earthquake Analysis</p></div></div><p class="text-xs text-slate-500 leading-relaxed">基于 USGS 地震目录，覆盖全球地震事件，提供震中定位、震级深度分析、区域活动趋势、事件属性对比，PostGIS 空间密度分析，DeepSeek AI 风险解读。</p></div>
        <div class="group bg-slate-50 rounded-3xl p-6 md:p-8 transition-all duration-500 hover:shadow-2xl hover:shadow-indigo-500/5 border border-slate-100 hover:border-indigo-200"><div class="flex items-start gap-4 mb-5"><div class="w-13 h-13 rounded-2xl bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/15 flex-shrink-0"><i class="fa fa-book text-white text-xl"></i></div><div><h3 class="text-base font-semibold text-slate-800 mb-0.5">学术文献检索</h3><p class="text-[11px] text-slate-400">Literature Search</p></div></div><p class="text-xs text-slate-500 leading-relaxed">支持标题、作者、分类、关键词及全文多维度检索。提供 PDF 上传与全文提取、引文网络分析、收藏管理、历史追溯、数据统计等功能。</p></div>
      </div>
    </div>
  </section>
  <footer class="bg-slate-900 text-white py-12"><div class="max-w-7xl mx-auto px-4 text-center"><div class="flex items-center justify-center gap-2 mb-3 text-slate-500"><i class="fa fa-cloud text-xs"></i><span class="text-xs tracking-wide">气象科学研究数据平台 v6.1</span></div><p class="text-slate-500 text-xs mb-1">&copy; 2026 南京农业大学 · 信息与计算科学专业</p><p class="text-slate-600 text-xs">丁俊杰 · hainuo@stu.njau.edu.cn</p></div></footer>
</div>
</template>
<script setup></script>
<style scoped>
@keyframes float-slow{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-30px) scale(1.05)}}
.animate-float-slow{animation:float-slow 12s ease-in-out infinite}
@keyframes float-delay{0%,100%{transform:translateY(0) scale(1)}50%{transform:translateY(-20px) scale(1.03)}}
.animate-float-delay{animation:float-delay 14s ease-in-out infinite 3s}
</style>