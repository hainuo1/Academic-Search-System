<template>
<div>
  <!-- ====== 英雄区域 ====== -->
  <section class="relative min-h-[80vh] flex items-center justify-center overflow-hidden">
    <div class="absolute inset-0 bg-gradient-to-br from-blue-600 via-indigo-700 to-purple-800 animate-gradient">
      <div class="absolute top-20 left-10 w-64 h-64 bg-white/5 rounded-full blur-2xl animate-float-slow"></div>
      <div class="absolute bottom-20 right-10 w-96 h-96 bg-white/5 rounded-full blur-2xl animate-float-delay"></div>
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-white/5 rounded-full blur-3xl animate-float-slower"></div>
    </div>

    <div class="relative z-10 max-w-4xl mx-auto px-6 text-center text-white">
      <!-- 校名标签 -->
      <div class="inline-block px-4 py-1.5 mb-6 bg-white/20 backdrop-blur-sm rounded-full text-sm font-medium tracking-wider border border-white/10">
        🏛️ 南京农业大学 · 学术文献检索系统
      </div>

      <!-- 主标题 -->
      <h1 class="text-4xl md:text-6xl lg:text-7xl font-bold mb-4 leading-tight">
        探索学术<span class="text-yellow-300">新</span>世界
      </h1>

      <!-- 副标题 -->
      <p class="text-xl md:text-2xl text-blue-100 mb-4">汇聚海量学术文献，智能检索 · 引用分析 · 数据洞察</p>

      <!-- 描述 -->
      <p class="text-base md:text-lg text-blue-50/80 max-w-2xl mx-auto mb-10 leading-relaxed">
        为学术研究提供一站式解决方案 —— 支持标题、作者、分类、关键词、全文五种检索方式，
        收藏管理、引用分析、数据统计，让您的学术探索更高效。
      </p>

      <!-- 登录 / 注册入口 -->
      <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
        <router-link to="/login"
          class="px-10 py-3.5 bg-white text-blue-700 font-semibold rounded-xl hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-0.5 text-lg shadow-lg">
          <i class="fa fa-sign-in mr-2"></i>登录
        </router-link>
        <router-link to="/register"
          class="px-10 py-3.5 bg-white/20 backdrop-blur-sm text-white font-semibold rounded-xl border border-white/30 hover:bg-white/30 transition-all duration-300 text-lg">
          <i class="fa fa-user-plus mr-2"></i>注册
        </router-link>
      </div>

      <p class="text-blue-200/60 text-sm mt-6">已有账号请登录，新用户请免费注册</p>
    </div>

    <!-- 底部滚动指示器 -->
    <div class="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 text-white/40 animate-bounce">
      <i class="fa fa-chevron-down text-xl"></i>
    </div>
  </section>

  <!-- ====== 核心功能卡片 ====== -->
  <section class="max-w-7xl mx-auto px-6 py-16">
    <div class="text-center mb-14">
      <h2 class="text-3xl md:text-4xl font-bold text-gray-800 mb-3">核心功能</h2>
      <p class="text-gray-500 text-base">为学术研究打造的完整工具链</p>
      <div class="w-16 h-1 bg-gradient-to-r from-blue-600 to-indigo-600 mx-auto mt-3 rounded-full"></div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- 智能检索 -->
      <div class="group bg-white rounded-2xl shadow-md hover:shadow-xl p-6 transition-all duration-300 transform hover:-translate-y-2 border border-gray-100/50 hover:border-blue-200">
        <div class="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg shadow-blue-500/20 group-hover:scale-110 transition-transform duration-300">
          <i class="fa fa-search text-white text-2xl"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-800 mb-2">智能检索</h3>
        <p class="text-gray-500 text-sm leading-relaxed">支持标题、作者、分类、关键词、全文五种检索方式，精准定位目标文献。</p>
      </div>

      <!-- 收藏管理 -->
      <div class="group bg-white rounded-2xl shadow-md hover:shadow-xl p-6 transition-all duration-300 transform hover:-translate-y-2 border border-gray-100/50 hover:border-yellow-200">
        <div class="w-14 h-14 bg-gradient-to-br from-yellow-400 to-yellow-500 rounded-2xl flex items-center justify-center mb-4 shadow-lg shadow-yellow-400/20 group-hover:scale-110 transition-transform duration-300">
          <i class="fa fa-star text-white text-2xl"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-800 mb-2">收藏管理</h3>
        <p class="text-gray-500 text-sm leading-relaxed">一键收藏感兴趣的文献，构建个人知识库，随时查阅，永不丢失。</p>
      </div>

      <!-- 引用分析 -->
      <div class="group bg-white rounded-2xl shadow-md hover:shadow-xl p-6 transition-all duration-300 transform hover:-translate-y-2 border border-gray-100/50 hover:border-purple-200">
        <div class="w-14 h-14 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg shadow-purple-500/20 group-hover:scale-110 transition-transform duration-300">
          <i class="fa fa-link text-white text-2xl"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-800 mb-2">引用分析</h3>
        <p class="text-gray-500 text-sm leading-relaxed">查看文献引用关系，追踪研究脉络，发现领域内的重要成果。</p>
      </div>

      <!-- 数据洞察 -->
      <div class="group bg-white rounded-2xl shadow-md hover:shadow-xl p-6 transition-all duration-300 transform hover:-translate-y-2 border border-gray-100/50 hover:border-green-200">
        <div class="w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg shadow-green-500/20 group-hover:scale-110 transition-transform duration-300">
          <i class="fa fa-bar-chart text-white text-2xl"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-800 mb-2">数据洞察</h3>
        <p class="text-gray-500 text-sm leading-relaxed">热门关键词、活跃用户、高被引文献 —— 多维数据，一目了然。</p>
      </div>

      <!-- 个人文献库 -->
      <div class="group bg-white rounded-2xl shadow-md hover:shadow-xl p-6 transition-all duration-300 transform hover:-translate-y-2 border border-gray-100/50 hover:border-indigo-200">
        <div class="w-14 h-14 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg shadow-indigo-500/20 group-hover:scale-110 transition-transform duration-300">
          <i class="fa fa-file-text text-white text-2xl"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-800 mb-2">个人文献库</h3>
        <p class="text-gray-500 text-sm leading-relaxed">上传、管理、编辑您的文献，构建专属学术资源中心。</p>
      </div>

      <!-- 历史记录 -->
      <div class="group bg-white rounded-2xl shadow-md hover:shadow-xl p-6 transition-all duration-300 transform hover:-translate-y-2 border border-gray-100/50 hover:border-gray-300">
        <div class="w-14 h-14 bg-gradient-to-br from-gray-600 to-gray-700 rounded-2xl flex items-center justify-center mb-4 shadow-lg shadow-gray-500/20 group-hover:scale-110 transition-transform duration-300">
          <i class="fa fa-history text-white text-2xl"></i>
        </div>
        <h3 class="text-lg font-semibold text-gray-800 mb-2">历史记录</h3>
        <p class="text-gray-500 text-sm leading-relaxed">检索历史 + 浏览历史，永不丢失您的学术探索足迹。</p>
      </div>
    </div>
  </section>

  <!-- ====== 数据统计展示 ====== -->
  <section class="bg-gray-50 py-16 border-t border-gray-100">
    <div class="max-w-7xl mx-auto px-6">
      <div class="grid grid-cols-3 gap-8 text-center">
        <div>
          <div class="text-4xl md:text-5xl font-bold text-blue-600">1000+</div>
          <div class="text-sm text-gray-500 mt-2">学术文献</div>
          <div class="text-xs text-gray-400 mt-1">涵盖多学科领域</div>
        </div>
        <div>
          <div class="text-4xl md:text-5xl font-bold text-indigo-600">10+</div>
          <div class="text-sm text-gray-500 mt-2">学科分类</div>
          <div class="text-xs text-gray-400 mt-1">人工智能、数据科学等</div>
        </div>
        <div>
          <div class="text-4xl md:text-5xl font-bold text-purple-600">100+</div>
          <div class="text-sm text-gray-500 mt-2">引用关系</div>
          <div class="text-xs text-gray-400 mt-1">追踪学术脉络</div>
        </div>
      </div>
    </div>
  </section>

  <!-- ====== 页脚 ====== -->
  <footer class="bg-gray-800 text-white py-8">
    <div class="max-w-7xl mx-auto px-4 text-center">
      <p class="text-gray-400 mb-2">&copy; 2026 南京农业大学 · 学术文献检索系统</p>
      <p class="text-gray-500 text-sm">信息与计算科学专业 · 毕设项目</p>
    </div>
  </footer>
</div>
</template>

<script setup>
</script>

<style scoped>
@keyframes gradient {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
.animate-gradient { background-size: 200% 200%; animation: gradient 6s ease infinite; }

@keyframes float-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}
.animate-float-slow { animation: float-slow 8s ease-in-out infinite; }

@keyframes float-delay {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}
.animate-float-delay { animation: float-delay 10s ease-in-out infinite 2s; }

@keyframes float-slower {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  50% { transform: translate(-50%, -50%) scale(1.05); }
}
.animate-float-slower { animation: float-slower 12s ease-in-out infinite 1s; }
</style>
