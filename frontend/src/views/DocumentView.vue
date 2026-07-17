<template>
<div class="max-w-4xl mx-auto px-4 py-10">
  <div v-if="loading" class="text-center py-24">
    <div class="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-6"></div>
    <p class="text-slate-500 text-lg">加载中...</p>
  </div>

  <template v-else-if="doc">
    <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-lg border border-slate-100 p-8 mb-8">
      <div class="flex items-start gap-4 mb-6 flex-wrap">
        <h1 class="text-2xl md:text-3xl font-bold text-slate-800 leading-snug flex-1 min-w-0">{{ doc.title }}</h1>
        <button @click="toggleFav"
          :class="fav ? 'bg-amber-50 border-amber-200 text-amber-600' : 'bg-slate-50 border-slate-200 text-slate-500 hover:border-amber-200 hover:text-amber-500'"
          class="flex items-center gap-2 px-5 py-2.5 rounded-xl border transition-all text-sm font-medium flex-shrink-0">
          <i :class="fav ? 'fa fa-star' : 'fa fa-star-o'"></i>
          <span>{{ fav ? '已收藏' : '收藏' }}</span>
        </button>
      </div>

      <div class="mb-6">
        <a href="#" @click.prevent="downloadPdf"
          class="inline-flex items-center gap-2 bg-gradient-to-r from-slate-800 to-indigo-900 text-white px-5 py-2.5 rounded-xl hover:shadow-lg hover:-translate-y-0.5 transition-all text-sm font-medium">
          <i class="fa fa-download"></i>下载全文
        </a>
        <p v-if="dlErr" class="text-red-500 text-sm mt-2 flex items-center gap-1"><i class="fa fa-exclamation-circle"></i>{{ dlErr }}</p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8 pb-8 border-b border-slate-100">
        <div class="flex items-center text-slate-600 text-sm"><i class="fa fa-user text-indigo-400 mr-2.5 w-5 text-center"></i><span class="font-medium text-slate-700">作者：</span><span class="ml-1.5">{{ doc.author }}</span></div>
        <div class="flex items-center text-slate-600 text-sm"><i class="fa fa-folder text-indigo-400 mr-2.5 w-5 text-center"></i><span class="font-medium text-slate-700">分类：</span><span class="ml-1.5">{{ doc.category }}</span></div>
        <div class="flex items-center text-slate-600 text-sm"><i class="fa fa-calendar text-indigo-400 mr-2.5 w-5 text-center"></i><span class="font-medium text-slate-700">发表日期：</span><span class="ml-1.5">{{ doc.publish_date }}</span></div>
        <div class="flex items-center text-slate-600 text-sm"><i class="fa fa-eye text-indigo-400 mr-2.5 w-5 text-center"></i><span class="font-medium text-slate-700">浏览次数：</span><span class="ml-1.5">{{ doc.view_count }}</span></div>
        <div class="flex items-center text-slate-600 text-sm"><i class="fa fa-download text-indigo-400 mr-2.5 w-5 text-center"></i><span class="font-medium text-slate-700">下载次数：</span><span class="ml-1.5">{{ doc.download_count }}</span></div>
      </div>

      <div class="flex items-start text-slate-600 mb-4 text-sm">
        <i class="fa fa-tags text-indigo-400 mr-2.5 mt-0.5 w-5 text-center"></i><span class="font-medium text-slate-700">关键词：</span>
        <div class="ml-1.5 flex flex-wrap gap-1.5">
          <span v-for="kw in keywords" :key="kw" class="bg-indigo-50 text-indigo-600 px-2.5 py-0.5 rounded-lg text-xs font-medium">{{ kw }}</span>
        </div>
      </div>

      <div class="flex items-center text-slate-600 mb-6 text-sm">
        <i class="fa fa-link text-indigo-400 mr-2.5 w-5 text-center"></i><span class="font-medium text-slate-700">被引次数：</span><span class="ml-1.5">{{ citCnt }}</span>
      </div>

      <div>
        <h2 class="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <span class="w-1 h-5 bg-indigo-500 rounded-full"></span>摘要
        </h2>
        <p class="text-slate-600 leading-relaxed text-sm">{{ doc.abstract }}</p>
      </div>
    </div>

    <div v-if="cits.length" class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-lg border border-slate-100 p-8">
      <h2 class="text-lg font-semibold text-slate-800 mb-6 flex items-center gap-2">
        <span class="w-1 h-5 bg-indigo-500 rounded-full"></span>
        <i class="fa fa-link text-indigo-400 mr-1"></i>引用本文的文献
      </h2>
      <div class="space-y-3">
        <router-link v-for="c in cits" :key="c.id" :to="`/document/${c.id}`"
          class="block p-4 bg-slate-50 rounded-xl hover:bg-indigo-50 transition-colors text-slate-700 hover:text-indigo-700 text-sm font-medium border border-transparent hover:border-indigo-100">
          {{ c.title }}
        </router-link>
      </div>
    </div>
  </template>

  <div v-else class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-16 text-center">
    <div class="w-24 h-24 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-6">
      <i class="fa fa-exclamation-circle text-red-400 text-4xl"></i>
    </div>
    <p class="text-slate-500 text-lg">文献不存在或已被删除</p>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const doc = ref(null); const keywords = ref([]); const cits = ref([]); const citCnt = ref(0); const fav = ref(false); const loading = ref(true); const dlErr = ref('')

onMounted(async () => {
  try {
    const r = await api.get(`/api/document/${route.params.id}`)
    if (r.data.code === 200) { const d = r.data.data; doc.value = d.document; keywords.value = d.keywords; cits.value = d.citations; citCnt.value = d.citation_count; fav.value = d.is_favorited }
    else doc.value = null
  } catch (e) { doc.value = null } finally { loading.value = false }
})

async function toggleFav() {
  try { const r = await api.post('/api/toggle_favorite', { document_id: route.params.id }); if (r.data.code === 200) fav.value = r.data.data.is_favorited } catch (e) {}
}

async function downloadPdf() {
  dlErr.value = ''
  try {
    const check = await api.get(`/api/download/${route.params.id}/check`)
    if (check.data.code !== 200) { dlErr.value = check.data.message; return }
    const token = localStorage.getItem('token')
    const link = document.createElement('a')
    link.href = `http://localhost:5000/api/download/${route.params.id}?token=${encodeURIComponent(token || '')}`
    document.body.appendChild(link); link.click(); document.body.removeChild(link)
  } catch (e) { dlErr.value = '文件不存在，可能已被删除' }
}
</script>
