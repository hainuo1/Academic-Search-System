<template>
<div class="max-w-4xl mx-auto px-4 py-12">
  <div class="bg-white/80 backdrop-blur-xl rounded-2xl shadow-md border border-slate-100 p-8">
    <div class="flex items-center gap-3 mb-6">
      <div class="w-10 h-10 bg-gradient-to-br from-slate-800 to-indigo-900 rounded-xl flex items-center justify-center">
        <i class="fa fa-pencil-square-o text-white text-lg"></i>
      </div>
      <div>
        <h2 class="text-2xl font-bold text-slate-800">编辑文献</h2>
        <p class="text-slate-500 text-sm">修改文献的元数据信息</p>
      </div>
    </div>

    <div v-if="err" class="mb-6 bg-red-50 border border-red-100 text-red-600 px-4 py-3 rounded-xl flex items-center text-sm">
      <i class="fa fa-exclamation-circle mr-2"></i>{{ err }}
    </div>

    <div v-if="loading" class="text-center py-16">
      <div class="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-4"></div>
      <p class="text-slate-500">加载中...</p>
    </div>

    <form v-else @submit.prevent="go">
      <div class="mb-6">
        <label class="block mb-2 font-medium text-slate-700 text-sm">标题 <span class="text-red-500">*</span></label>
        <input v-model="t" type="text" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
      </div>
      <div class="mb-6">
        <label class="block mb-2 font-medium text-slate-700 text-sm">作者 <span class="text-red-500">*</span></label>
        <input v-model="a" type="text" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
      </div>
      <div class="mb-6">
        <label class="block mb-2 font-medium text-slate-700 text-sm">分类 <span class="text-red-500">*</span></label>
        <input v-model="c" type="text" placeholder="例如：人工智能、数据库、信息检索" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
      </div>
      <div class="mb-6">
        <label class="block mb-2 font-medium text-slate-700 text-sm">发表日期 <span class="text-red-500">*</span></label>
        <input v-model="pd" type="date" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
      </div>
      <div class="mb-6">
        <label class="block mb-2 font-medium text-slate-700 text-sm">关键词 <span class="text-red-500">*</span></label>
        <input v-model="kw" type="text" placeholder="例如：AI;机器学习;知识图谱" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none">
        <p class="text-slate-500 text-sm mt-1">多个关键词用分号分隔</p>
      </div>
      <div class="mb-8">
        <label class="block mb-2 font-medium text-slate-700 text-sm">摘要 <span class="text-red-500">*</span></label>
        <textarea v-model="ab" rows="6" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:border-indigo-400 focus:ring-4 focus:ring-indigo-50 transition-all outline-none"></textarea>
      </div>

      <div class="flex gap-4">
        <button type="submit" :disabled="ld"
          class="px-8 py-3 bg-gradient-to-r from-slate-800 to-indigo-900 text-white rounded-2xl font-medium shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all flex items-center justify-center gap-2">
          <span v-if="ld"><i class="fa fa-spinner fa-spin mr-2"></i>保存中...</span>
          <span v-else><i class="fa fa-save mr-2"></i>保存修改</span>
        </button>
        <router-link to="/my_documents" class="px-8 py-3 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-2xl font-medium transition-all">取消</router-link>
      </div>
    </form>
  </div>
</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFlashStore } from '../stores/flash'
import api from '../api'

const route = useRoute(); const router = useRouter(); const flash = useFlashStore()
const t = ref(''); const a = ref(''); const c = ref(''); const pd = ref(''); const kw = ref(''); const ab = ref('')
const err = ref(''); const loading = ref(true); const ld = ref(false)

onMounted(async () => {
  try {
    const r = await api.get(`/api/document/${route.params.id}`)
    if (r.data.code === 200) { const d = r.data.data.document; t.value = d.title; a.value = d.author; c.value = d.category; pd.value = d.publish_date; kw.value = d.keywords; ab.value = d.abstract }
    else err.value = '加载文献信息失败'
  } catch (e) { err.value = '加载文献信息失败' } finally { loading.value = false }
})

async function go() {
  err.value = ''; ld.value = true
  try {
    const r = await api.put(`/api/document/${route.params.id}`, { title: t.value, author: a.value, category: c.value, publish_date: pd.value, keywords: kw.value, abstract: ab.value })
    if (r.data.code === 200) { flash.show('修改保存成功', 'success'); router.push('/my_documents') }
    else err.value = r.data.message
  } catch (e) { err.value = e.response?.data?.message || '保存失败' } finally { ld.value = false }
}
</script>
