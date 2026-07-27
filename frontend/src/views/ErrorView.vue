<template>
<div class="max-w-2xl mx-auto py-20 px-6">
  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-10 text-center">
    <div class="w-20 h-20 bg-gradient-to-br from-red-50 to-rose-50 rounded-full flex items-center justify-center mx-auto mb-6">
      <i class="fa fa-exclamation-circle text-red-400 text-4xl"></i>
    </div>
    <h1 class="text-3xl font-bold text-slate-800 mb-3">系统提示</h1>
    <p class="text-slate-500 text-lg mb-8">您访问的页面不存在，请检查链接是否正确。</p>
    <div class="flex justify-center gap-4">
      <router-link to="/search" class="px-6 py-3 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all">返回首页</router-link>
      <button @click="$router.go(-1)" class="px-6 py-3 bg-slate-100 text-slate-600 rounded-2xl font-medium hover:bg-slate-200 hover:-translate-y-0.5 transition-all">返回上一页</button>
    </div>
  </div>
</div>
</template>
