<template>
<div class="max-w-4xl mx-auto px-4 py-8">
  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-6 md:p-8">
    <div class="flex items-center gap-3 mb-6 pb-4 border-b border-slate-100">
      <div class="w-10 h-10 bg-gradient-to-br from-slate-800 to-indigo-900 rounded-xl flex items-center justify-center">
        <i class="fa fa-link text-white text-lg"></i>
      </div>
      <div>
        <h2 class="text-2xl font-bold text-slate-800">设置引用关系</h2>
        <p class="text-slate-500 text-sm">为当前文献添加引用关系</p>
      </div>
    </div>

    <div class="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-4 mb-6 border border-indigo-100 flex items-center gap-3">
      <i class="fa fa-file-text-o text-indigo-500"></i>
      <span class="text-sm text-slate-700">当前文献：<strong class="text-slate-800">{{ cd?.title }}</strong></span>
    </div>

    <div v-if="err" class="mb-4 px-4 py-3 bg-red-50 border border-red-100 text-red-600 rounded-xl text-sm flex items-center">
      <i class="fa fa-exclamation-circle mr-2"></i>{{ err }}
    </div>

    <div class="mb-4">
      <div class="relative">
        <span class="absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400">
          <i class="fa fa-search"></i>
        </span>
        <input v-model="skw" type="text" @keyup.enter="searchCit" placeholder="输入标题搜索文献"
          class="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
      </div>
    </div>

    <button @click="searchCit" class="px-5 py-2.5 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-xl font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all text-sm">搜索文献</button>

    <!-- 搜索结果 -->
    <div v-if="sres.length" class="mt-6 space-y-2">
      <div v-for="d in sres" :key="d.id" class="flex justify-between items-center p-4 bg-slate-50 rounded-xl border border-slate-100 hover:border-indigo-200 transition-all">
        <div><span class="text-slate-800 font-medium">{{ d.title }}</span><span class="text-slate-400 text-sm ml-2">{{ d.author }}</span></div>
        <button @click="add(d)" class="px-4 py-1.5 bg-indigo-50 text-indigo-600 rounded-lg text-sm font-medium hover:bg-indigo-100 transition whitespace-nowrap">添加引用</button>
      </div>
    </div>
    <p v-if="searched && !sres.length" class="text-slate-400 py-6 text-center">未找到匹配的文献</p>

    <!-- 已选引用 -->
    <div v-if="sel.length" class="mt-6">
      <h3 class="text-base font-semibold text-slate-700 mb-3 flex items-center gap-2">
        <i class="fa fa-check-circle text-emerald-500"></i>已选引用文献
      </h3>
      <div class="space-y-2">
        <div v-for="d in sel" :key="d.id" class="flex justify-between items-center p-4 bg-gradient-to-r from-indigo-50 to-blue-50 rounded-xl border border-indigo-100">
          <router-link :to="`/document/${d.id}`" class="text-indigo-600 hover:text-indigo-800 font-medium text-sm transition-colors">{{ d.title }}</router-link>
          <button @click="rm(d.id)" class="w-8 h-8 bg-white/80 rounded-lg flex items-center justify-center text-red-400 hover:text-red-600 hover:bg-red-50 transition-all"><i class="fa fa-times"></i></button>
        </div>
      </div>
    </div>

    <button @click="saveCit" class="mt-6 px-6 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all text-sm">
      <i class="fa fa-floppy-o mr-2"></i>保存引用关系
    </button>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFlashStore } from '../stores/flash'
import api from '../api'

const route = useRoute(); const router = useRouter(); const flash = useFlashStore()
const cd = ref(null); const sel = ref([]); const skw = ref(''); const sres = ref([]); const searched = ref(false); const err = ref('')

onMounted(async () => { try { const r = await api.get(`/api/citation/${route.params.id}`); if (r.data.code === 200) cd.value = r.data.data.current_doc; else err.value = r.data.message } catch (e) { err.value = e.response?.data?.message || '加载失败' } })

async function searchCit() { if (!skw.value.trim()) return; searched.value = true; try { const r = await api.get('/api/search_citation', { params: { keyword: skw.value.trim(), doc_id: route.params.id } }); if (r.data.code === 200) sres.value = r.data.data.results } catch (e) { console.error('搜索引用文献失败:', e) } }

function add(d) { if (!sel.value.find(x => x.id === d.id)) sel.value.push(d) }
function rm(id) { sel.value = sel.value.filter(x => x.id !== id) }

async function saveCit() {
  try {
    const r = await api.post(`/api/save_citation/${route.params.id}`, { target_doc_ids: sel.value.map(d => d.id) })
    if (r.data.code === 200) { flash.show('引用关系已保存', 'success'); router.push('/my_documents') }
    else err.value = r.data.message
  } catch (e) { err.value = e.response?.data?.message || '保存失败' }
}
</script>
