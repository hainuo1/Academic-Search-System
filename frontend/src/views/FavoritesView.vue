<template>
<div class="max-w-6xl mx-auto px-4 py-8">
  <div class="mb-8">
    <div class="flex items-center mb-2">
      <div class="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center mr-3 shadow-md">
        <i class="fa fa-star text-white text-lg"></i>
      </div>
      <div>
        <h1 class="text-2xl font-bold text-slate-800">我的收藏</h1>
        <p class="text-slate-500 text-sm">收藏您感兴趣的文献，方便随时查阅</p>
      </div>
    </div>
  </div>

  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100">
    <div class="p-6 md:p-8">
      <div class="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
        <span class="text-sm text-slate-500">共 {{ totalCount }} 篇收藏</span>
      </div>

      <div v-if="docs.length" class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-slate-50">
              <th class="text-left py-3 px-4 font-semibold text-sm text-slate-600">ID</th>
              <th class="text-left py-3 px-4 font-semibold text-sm text-slate-600">标题</th>
              <th class="text-left py-3 px-4 font-semibold text-sm text-slate-600">作者</th>
              <th class="text-left py-3 px-4 font-semibold text-sm text-slate-600">发表日期</th>
              <th class="text-left py-3 px-4 font-semibold text-sm text-slate-600">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in docs" :key="d.id" class="hover:bg-slate-50 border-b border-slate-50 last:border-0">
              <td class="py-3 px-4 text-sm text-slate-500">{{ d.id }}</td>
              <td class="py-3 px-4 text-sm text-slate-800">
                <router-link :to="`/document/${d.id}`" class="text-indigo-600 hover:text-indigo-800 font-medium transition-colors">{{ d.title }}</router-link>
              </td>
              <td class="py-3 px-4 text-sm text-slate-500">{{ d.author }}</td>
              <td class="py-3 px-4 text-sm text-slate-500">{{ d.publish_date }}</td>
              <td class="py-3 px-4">
                <div class="flex flex-wrap gap-1.5">
                  <router-link :to="`/document/${d.id}`" class="bg-indigo-50 text-indigo-600 hover:bg-indigo-100 px-3 py-1.5 rounded-lg text-xs font-medium transition whitespace-nowrap">查看</router-link>
                  <a href="#" @click.prevent="downloadPdf(d.id)" class="bg-emerald-50 text-emerald-600 hover:bg-emerald-100 px-3 py-1.5 rounded-lg text-xs font-medium transition whitespace-nowrap">下载</a>
                  <button @click="rm(d)" class="bg-amber-50 text-amber-600 hover:bg-amber-100 px-3 py-1.5 rounded-lg text-xs font-medium transition whitespace-nowrap">取消收藏</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="tps > 1" class="mt-8 pt-6 border-t border-slate-100">
        <div class="text-center text-slate-500 text-sm mb-4">共 {{ totalCount }} 篇 · 第 {{ pg }} / {{ tps }} 页</div>
        <div class="flex justify-center items-center gap-2 flex-wrap">
          <button v-if="pg > 1" @click="load(pg - 1)" class="px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm hover:bg-slate-50 transition-all shadow-sm font-medium text-slate-600">← 上一页</button>
          <button v-for="p in vp" :key="p" @click="load(p)"
            :class="p === pg ? 'bg-gradient-to-r from-slate-800 to-indigo-900 text-white border-transparent shadow-lg' : 'bg-white border-slate-200 hover:bg-slate-50 text-slate-600'"
            class="px-4 py-2.5 rounded-xl text-sm border transition-all shadow-sm font-medium min-w-[44px]">{{ p }}</button>
          <button v-if="pg < tps" @click="load(pg + 1)" class="px-4 py-2.5 bg-white border border-slate-200 rounded-xl text-sm hover:bg-slate-50 transition-all shadow-sm font-medium text-slate-600">下一页 →</button>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!docs.length" class="text-center py-16">
        <div class="w-24 h-24 bg-gradient-to-br from-amber-50 to-orange-50 rounded-full flex items-center justify-center mx-auto mb-6">
          <i class="fa fa-star-o text-amber-400 text-4xl"></i>
        </div>
        <h3 class="text-xl font-bold text-slate-700 mb-2">暂无收藏</h3>
        <p class="text-slate-500 mb-6">您还没有收藏任何文献，去浏览文献，把有用的收藏起来吧！</p>
        <router-link to="/search" class="px-6 py-3 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-2xl text-sm font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all inline-block">去检索文献</router-link>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
const docs = ref([]); const pg = ref(1); const tps = ref(1); const totalCount = ref(0)
const vp = computed(() => { const a = []; for (let i = Math.max(1, pg.value - 2); i <= Math.min(tps.value, pg.value + 2); i++) a.push(i); return a })
async function load(p) { try { const r = await api.get('/api/favorites', { params: { page: p } }); if (r.data.code === 200) { docs.value = r.data.data.documents; pg.value = r.data.data.page; tps.value = r.data.data.total_pages; totalCount.value = r.data.data.total_count } } catch (e) { console.error('加载收藏失败:', e) } }
async function rm(d) { try { const r = await api.post('/api/toggle_favorite', { document_id: d.id }); if (r.data.code === 200 && !r.data.data.is_favorited) { docs.value = docs.value.filter(x => x.id !== d.id); totalCount.value-- } } catch (e) { console.error('取消收藏失败:', e) } }
async function downloadPdf(docId) {
  try {
    const resp = await api.get(`/api/download/${docId}`, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([resp.data]))
    const link = document.createElement('a')
    link.href = url
    const disposition = resp.headers['content-disposition']
    link.download = disposition ? decodeURIComponent(disposition.split("filename*=UTF-8''")[1] || disposition.split('filename=')[1] || 'document.pdf') : 'document.pdf'
    document.body.appendChild(link); link.click(); document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (e) { alert('下载失败，请稍后重试') }
}
onMounted(() => load(1))
</script>
